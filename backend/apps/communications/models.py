from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Channel(TimeStampedModel):
    class Kind(models.TextChoices):
        GENERAL = "general", "General"
        ANNOUNCEMENTS = "announcements", "Announcements"
        ORDER = "order", "Order"
        SUPPORT = "support", "Support"

    name = models.CharField(max_length=120, unique=True)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.GENERAL)
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_channels"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Conversation(TimeStampedModel):
    class Kind(models.TextChoices):
        DIRECT = "direct", "Direct"
        ORDER = "order", "Order"
        RFQ = "rfq", "RFQ"
        SUPPORT = "support", "Support"

    title = models.CharField(max_length=180, blank=True)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.DIRECT)
    entity_id = models.CharField(max_length=64, blank=True)
    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations"
    )
    is_closed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_conversations"
    )

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class ConversationParticipant(TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_participations")
    last_read_at = models.DateTimeField(null=True, blank=True)
    is_muted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("conversation", "user")


class Message(TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    thread = models.ForeignKey(
        "Thread", null=True, blank=True, on_delete=models.SET_NULL, related_name="messages"
    )
    body = models.TextField()
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)


class Thread(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="threads")
    title = models.CharField(max_length=180)
    starter_message = models.ForeignKey(
        Message, null=True, blank=True, on_delete=models.SET_NULL, related_name="threads_started"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    is_pinned = models.BooleanField(default=False)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="closed_threads"
    )
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title


class MessageReaction(TimeStampedModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_reactions")
    emoji = models.CharField(max_length=32)

    class Meta:
        unique_together = ("message", "user", "emoji")

    def __str__(self):
        return f"{self.emoji} by {self.user_id}"


class ReadReceipt(TimeStampedModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="read_receipts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="read_receipts")
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"Read {self.message_id} by {self.user_id}"


class CannedResponse(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="canned_responses"
    )
    title = models.CharField(max_length=180)
    body = models.TextField()
    shortcut = models.CharField(max_length=32, blank=True)
    is_shared = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class MessageTemplate(TimeStampedModel):
    class ChannelKind(models.TextChoices):
        EMAIL = "email", "Email"
        PUSH = "push", "Push"
        SMS = "sms", "SMS"
        IN_APP = "in_app", "In app"

    name = models.CharField(max_length=160)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    channel_kind = models.CharField(max_length=16, choices=ChannelKind.choices, default=ChannelKind.EMAIL)
    variables = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Attachment(TimeStampedModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    content_type = models.CharField(max_length=120, blank=True)


class OrderDiscussion(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"

    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="order_discussion")
    order_id = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


class Notification(TimeStampedModel):
    class Level(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ACTION = "action", "Action"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    level = models.CharField(max_length=16, choices=Level.choices, default=Level.INFO)
    link = models.URLField(blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_read(self):
        return self.read_at is None


class NotificationPreference(TimeStampedModel):
    class DigestFrequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        NEVER = "never", "Never"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preference")
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    push_channels = models.JSONField(default=list, blank=True)
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(max_length=16, choices=DigestFrequency.choices, default=DigestFrequency.DAILY)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)


class Dispute(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In review"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    conversation = models.ForeignKey(
        Conversation, null=True, blank=True, on_delete=models.SET_NULL, related_name="disputes"
    )
    order_id = models.PositiveIntegerField(null=True, blank=True)
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="opened_disputes")
    subject = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


class SearchIndex(TimeStampedModel):
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["entity_type", "entity_id"])]


class SearchEvent(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_events")
    query = models.CharField(max_length=255)
    result_count = models.PositiveIntegerField(default=0)
    filters = models.JSONField(default=dict, blank=True)
