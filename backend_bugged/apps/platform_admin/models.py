from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PlatformSetting(TimeStampedModel):
    key = models.CharField(max_length=120, unique=True)
    value = models.CharField(default=dict, blank=True)
    description = models.TextField(blank=True)


class FeatureFlag(TimeStampedModel):
    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    audience = models.JSONField(default=dict, blank=True)


class OperationalSla(TimeStampedModel):
    module = models.CharField(max_length=80)
    name = models.CharField(max_length=160)
    target_hours = models.PositiveIntegerField(default=24)
    active = models.BooleanField(default=True)


class SupportTicket(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_ticketss_ref")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets"
    )
    subject = models.CharField(max_length=180)
    body = models.TextField()
    module = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.NORMAL)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


class SupportTicketComment(TimeStampedModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    internal = models.BooleanField(default=False)


class ModerationCase(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACTIONED = "actioned", "Actioned"
        DISMISSED = "dismissed", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderation_reports"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderation_cases"
    )
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=64)
    reason = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    decision = models.CharField(max_length=80, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)


class DataExportJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="export_jobs")
    export_type = models.CharField(max_length=80)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    file_url = models.URLField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class SystemAnnouncement(TimeStampedModel):
    title = models.CharField(max_length=180)
    body = models.TextField()
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
