import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def _oauth_client_id():
    return f"tl_{uuid.uuid4().hex[:24]}"


def _oauth_secret():
    return secrets.token_urlsafe(32)


class APIClient(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_clients")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class APIKey(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"

    client = models.ForeignKey(APIClient, on_delete=models.CASCADE, related_name="keys")
    prefix = models.CharField(max_length=12)
    hashed_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class OAuthApplication(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="oauth_applications"
    )
    name = models.CharField(max_length=160)
    client_id = models.CharField(max_length=64, unique=True, default=_oauth_client_id)
    client_secret = models.CharField(max_length=128, default=_oauth_secret)
    scopes = models.JSONField(default=list, blank=True)
    redirect_uris = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class OAuthGrant(TimeStampedModel):
    application = models.ForeignKey(OAuthApplication, on_delete=models.CASCADE, related_name="grants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="oauth_grants")
    access_token = models.CharField(max_length=128, blank=True)
    refresh_token = models.CharField(max_length=128, blank=True)
    scopes = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_active(self):
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at >= timezone.now():
            return False
        return True


class RetryPolicy(TimeStampedModel):
    name = models.CharField(max_length=80)
    max_attempts = models.PositiveIntegerField(default=5)
    backoff_seconds = models.PositiveIntegerField(default=30)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class WebhookEndpoint(TimeStampedModel):
    client = models.ForeignKey(APIClient, on_delete=models.CASCADE, related_name="webhook_endpoints")
    url = models.URLField()
    secret = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)


class WebhookSubscription(TimeStampedModel):
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="subscriptions")
    event_type = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("endpoint", "event_type")


class WebhookDelivery(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    response_code = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class IntegrationHealthCheck(TimeStampedModel):
    class Status(models.TextChoices):
        OK = "ok", "OK"
        DEGRADED = "degraded", "Degraded"
        DOWN = "down", "Down"

    integration_name = models.CharField(max_length=120)
    component = models.CharField(max_length=120, default="api")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OK)
    latency_ms = models.PositiveIntegerField(default=0)
    checked_at = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-checked_at",)

    def __str__(self):
        return f"{self.integration_name}/{self.component} {self.status}"


class PayloadSchema(TimeStampedModel):
    name = models.CharField(max_length=160)
    event_type = models.CharField(max_length=80)
    version = models.CharField(max_length=20, default="1.0")
    schema = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        unique_together = ("event_type", "version")

    def __str__(self):
        return f"{self.name} v{self.version}"


class EDIPartner(TimeStampedModel):
    name = models.CharField(max_length=160)
    qualifier = models.CharField(max_length=20, blank=True)
    identifier = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)


class EDIDocument(TimeStampedModel):
    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    partner = models.ForeignKey(EDIPartner, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=40)
    direction = models.CharField(max_length=16, choices=Direction.choices)
    payload = models.TextField(blank=True)
    reference = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ("-created_at",)


class ERPConnector(TimeStampedModel):
    class Status(models.TextChoices):
        DISCONNECTED = "disconnected", "Disconnected"
        CONNECTED = "connected", "Connected"
        ERROR = "error", "Error"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="erp_connectors")
    name = models.CharField(max_length=160)
    system = models.CharField(max_length=80, default="generic")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DISCONNECTED)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)


class SFTPDropbox(TimeStampedModel):
    name = models.CharField(max_length=160)
    host = models.CharField(max_length=180)
    path = models.CharField(max_length=255, default="/inbound")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)


class MappingTemplate(TimeStampedModel):
    name = models.CharField(max_length=160)
    source_format = models.CharField(max_length=40)
    target_format = models.CharField(max_length=40)
    mapping = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class FieldMapping(TimeStampedModel):
    template = models.ForeignKey(MappingTemplate, on_delete=models.CASCADE, related_name="field_mappings")
    source_field = models.CharField(max_length=120)
    target_field = models.CharField(max_length=120)
    transform = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("template", "target_field")
        unique_together = ("template", "source_field", "target_field")


class CatalogImportJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    connector = models.ForeignKey(ERPConnector, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    source = models.CharField(max_length=180, blank=True)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)


class PriceSyncJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    connector = models.ForeignKey(ERPConnector, on_delete=models.PROTECT, related_name="price_syncs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)


class InventorySyncJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    connector = models.ForeignKey(ERPConnector, on_delete=models.CASCADE, related_name="inventory_syncs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)


class AutomationRule(TimeStampedModel):
    name = models.CharField(max_length=160)
    event_type = models.CharField(max_length=80)
    action = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)


class IntegrationEvent(TimeStampedModel):
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ("-created_at",)


class IntegrationAuditLog(TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="integration_audit_logs"
    )
    action = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=64, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.action} {self.resource_type}:{self.resource_id}"


class DeadLetterRecord(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REDRIVEN = "redriven", "Redriven"
        RESOLVED = "resolved", "Resolved"

    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    attempts = models.PositiveIntegerField(default=0)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
