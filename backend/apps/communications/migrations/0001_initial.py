import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TimeStampedModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("general", "General"),
                            ("announcements", "Announcements"),
                            ("order", "Order"),
                            ("support", "Support"),
                        ],
                        default="general",
                        max_length=16,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("is_private", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_channels",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Conversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(blank=True, max_length=180)),
                (
                    "kind",
                    models.CharField(
                        choices=[("direct", "Direct"), ("order", "Order"), ("rfq", "RFQ"), ("support", "Support")],
                        default="direct",
                        max_length=16,
                    ),
                ),
                ("entity_id", models.CharField(blank=True, max_length=64)),
                ("is_closed", models.BooleanField(default=False)),
                (
                    "channel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="conversations",
                        to="communications.channel",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_conversations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ConversationParticipant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_read_at", models.DateTimeField(blank=True, null=True)),
                ("is_muted", models.BooleanField(default=False)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participants",
                        to="communications.conversation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conversation_participations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("conversation", "user")},
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Thread",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("closed", "Closed")], default="open", max_length=16
                    ),
                ),
                ("is_pinned", models.BooleanField(default=False)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "closed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="closed_threads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="threads",
                        to="communications.conversation",
                    ),
                ),
                (
                    "starter_message",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="threads_started",
                        to="communications.message",
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("body", models.TextField()),
                ("is_system", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="messages", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="communications.conversation",
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="messages",
                        to="communications.thread",
                    ),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="MessageReaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("emoji", models.CharField(max_length=32)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reactions",
                        to="communications.message",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="message_reactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("message", "user", "emoji")},
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReadReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("read_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="read_receipts",
                        to="communications.message",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="read_receipts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("message", "user")},
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CannedResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("body", models.TextField()),
                ("shortcut", models.CharField(blank=True, max_length=32)),
                ("is_shared", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="canned_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("title",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="MessageTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("subject", models.CharField(blank=True, max_length=180)),
                ("body", models.TextField()),
                (
                    "channel_kind",
                    models.CharField(
                        choices=[("email", "Email"), ("push", "Push"), ("sms", "SMS"), ("in_app", "In app")],
                        default="email",
                        max_length=16,
                    ),
                ),
                ("variables", models.JSONField(blank=True, default=list)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file_name", models.CharField(max_length=255)),
                ("file_url", models.URLField()),
                ("content_type", models.CharField(blank=True, max_length=120)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="communications.message",
                    ),
                ),
            ],
            options={},
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="OrderDiscussion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("resolved", "Resolved")], default="open", max_length=16
                    ),
                ),
                ("resolution", models.TextField(blank=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "conversation",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_discussion",
                        to="communications.conversation",
                    ),
                ),
            ],
            options={},
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("body", models.TextField(blank=True)),
                (
                    "level",
                    models.CharField(
                        choices=[("info", "Info"), ("warning", "Warning"), ("action", "Action")],
                        default="info",
                        max_length=16,
                    ),
                ),
                ("link", models.CharField(blank=True, max_length=255)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email_enabled", models.BooleanField(default=True)),
                ("push_enabled", models.BooleanField(default=True)),
                ("in_app_enabled", models.BooleanField(default=True)),
                ("push_channels", models.JSONField(blank=True, default=list)),
                ("digest_enabled", models.BooleanField(default=False)),
                (
                    "digest_frequency",
                    models.CharField(
                        choices=[("daily", "Daily"), ("weekly", "Weekly"), ("never", "Never")],
                        default="daily",
                        max_length=16,
                    ),
                ),
                ("quiet_hours_start", models.TimeField(blank=True, null=True)),
                ("quiet_hours_end", models.TimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_preference",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Dispute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.PositiveIntegerField(blank=True, null=True)),
                ("subject", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In review"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("resolution", models.TextField(blank=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "conversation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="disputes",
                        to="communications.conversation",
                    ),
                ),
                (
                    "opened_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opened_disputes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SearchIndex",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("entity_type", models.CharField(max_length=80)),
                ("entity_id", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "indexes": [models.Index(fields=["entity_type", "entity_id"], name="communicat_entity__0ba0ff_idx")],
            },
            bases=("communications", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SearchEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("query", models.CharField(max_length=255)),
                ("result_count", models.PositiveIntegerField(default=0)),
                ("filters", models.JSONField(blank=True, default=dict)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="search_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("communications", "TimeStampedModel"),
        ),
    ]
