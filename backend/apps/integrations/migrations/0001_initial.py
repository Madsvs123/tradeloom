import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import apps.integrations.models


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
            name="APIClient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_clients",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("prefix", models.CharField(max_length=12)),
                ("hashed_key", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("revoked", "Revoked")], default="active", max_length=16
                    ),
                ),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="keys", to="integrations.apiclient"
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="OAuthApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                (
                    "client_id",
                    models.CharField(
                        default=apps.integrations.models._oauth_client_id, max_length=64, unique=True
                    ),
                ),
                ("client_secret", models.CharField(default=apps.integrations.models._oauth_secret, max_length=128)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("redirect_uris", models.JSONField(blank=True, default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("revoked", "Revoked")], default="active", max_length=16
                    ),
                ),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="oauth_applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="OAuthGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("access_token", models.CharField(blank=True, max_length=128)),
                ("refresh_token", models.CharField(blank=True, max_length=128)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grants",
                        to="integrations.oauthapplication",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="oauth_grants",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RetryPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("max_attempts", models.PositiveIntegerField(default=5)),
                ("backoff_seconds", models.PositiveIntegerField(default=30)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WebhookEndpoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.URLField()),
                ("secret", models.CharField(blank=True, max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhook_endpoints",
                        to="integrations.apiclient",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WebhookSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "endpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="integrations.webhookendpoint",
                    ),
                ),
            ],
            options={
                "unique_together": {("endpoint", "event_type")},
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WebhookDelivery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(max_length=80)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("delivered", "Delivered"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("response_code", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "endpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deliveries",
                        to="integrations.webhookendpoint",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="IntegrationHealthCheck",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("integration_name", models.CharField(max_length=120)),
                ("component", models.CharField(default="api", max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[("ok", "OK"), ("degraded", "Degraded"), ("down", "Down")],
                        default="ok",
                        max_length=16,
                    ),
                ),
                ("latency_ms", models.PositiveIntegerField(default=0)),
                ("checked_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("details", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("-checked_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PayloadSchema",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("event_type", models.CharField(max_length=80)),
                ("version", models.CharField(default="1.0", max_length=20)),
                ("schema", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
                "unique_together": {("event_type", "version")},
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="EDIPartner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("qualifier", models.CharField(blank=True, max_length=20)),
                ("identifier", models.CharField(blank=True, max_length=80)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="EDIDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("document_type", models.CharField(max_length=40)),
                (
                    "direction",
                    models.CharField(
                        choices=[("inbound", "Inbound"), ("outbound", "Outbound")], max_length=16
                    ),
                ),
                ("payload", models.TextField(blank=True)),
                ("reference", models.CharField(blank=True, max_length=80)),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="integrations.edipartner",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ERPConnector",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("system", models.CharField(default="generic", max_length=80)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("disconnected", "Disconnected"),
                            ("connected", "Connected"),
                            ("error", "Error"),
                        ],
                        default="disconnected",
                        max_length=16,
                    ),
                ),
                ("config", models.JSONField(blank=True, default=dict)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="erp_connectors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SFTPDropbox",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("host", models.CharField(max_length=180)),
                ("path", models.CharField(default="/inbound", max_length=255)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="MappingTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("source_format", models.CharField(max_length=40)),
                ("target_format", models.CharField(max_length=40)),
                ("mapping", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="FieldMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_field", models.CharField(max_length=120)),
                ("target_field", models.CharField(max_length=120)),
                ("transform", models.CharField(blank=True, max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="field_mappings",
                        to="integrations.mappingtemplate",
                    ),
                ),
            ],
            options={
                "ordering": ("template", "target_field"),
                "unique_together": {("template", "source_field", "target_field")},
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CatalogImportJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=16,
                    ),
                ),
                ("source", models.CharField(blank=True, max_length=180)),
                ("stats", models.JSONField(blank=True, default=dict)),
                (
                    "connector",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="integrations.erpconnector",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PriceSyncJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=16,
                    ),
                ),
                ("stats", models.JSONField(blank=True, default=dict)),
                (
                    "connector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_syncs",
                        to="integrations.erpconnector",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InventorySyncJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=16,
                    ),
                ),
                ("stats", models.JSONField(blank=True, default=dict)),
                (
                    "connector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory_syncs",
                        to="integrations.erpconnector",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="AutomationRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("event_type", models.CharField(max_length=80)),
                ("action", models.CharField(max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                ("config", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="IntegrationEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(max_length=80)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("source", models.CharField(blank=True, max_length=80)),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="IntegrationAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(max_length=80)),
                ("resource_type", models.CharField(max_length=80)),
                ("resource_id", models.CharField(blank=True, max_length=64)),
                ("details", models.JSONField(blank=True, default=dict)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="integration_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="DeadLetterRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(max_length=80)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("error", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("redriven", "Redriven"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("integrations", "TimeStampedModel"),
        ),
    ]
