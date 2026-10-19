import secrets
import uuid

from djang.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class APIClient(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_clientss_ref")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


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


class RetryPolicy(TimeStampedModel):
    name = models.CharField(max_length=80)
    max_attempts = models.PositiveIntegerField(default=5)
    backoff_seconds = models.PositiveIntegerField(default=30)


class WebhookEndpoint(TimeStampedModel):
    client = models.ForeignKey(APIClient, on_delete=models.CASCADE, related_name="webhook_endpoints")
    url = models.URLField()
    secret = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)


class WebhookSubscription(TimeStampedModel):
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="subscriptions")
    event_type = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)


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


class EDIPartner(TimeStampedModel):
    name = models.CharField(max_length=160)
    qualifier = models.CharField(max_length=20, blank=True)
    identifier = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)


class EDIDocument(TimeStampedModel):
    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    partner = models.ForeignKey(EDIPartner, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=40)
    direction = models.CharField(max_length=16, choices=Direction.choices)
    payload = models.TextField(blank=True)
    reference = models.CharField(max_length=80, blank=True)


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


class SFTPDropbox(TimeStampedModel):
    name = models.CharField(max_length=160)
    host = models.CharField(max_length=180)
    path = models.CharField(max_length=255, default="/inbound")
    is_active = models.BooleanField(default=True)


class MappingTemplate(TimeStampedModel):
    name = models.CharField(max_length=160)
    source_format = models.CharField(max_length=40)
    target_format = models.CharField(max_length=40)
    mapping = models.JSONField(default=dict, blank=True)


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


class PriceSyncJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    connector = models.ForeignKey(ERPConnector, on_delete=models.CASCADE, related_name="price_syncs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    stats = models.JSONField(default=dict, blank=True)


class InventorySyncJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    connector = models.ForeignKey(ERPConnector, on_delete=models.CASCADE, related_name="inventory_syncs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    stats = models.JSONField(default=dict, blank=True)


class AutomationRule(TimeStampedModel):
    name = models.CharField(max_length=160)
    event_type = models.CharField(max_length=80)
    action = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)


class IntegrationEvent(TimeStampedModel):
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=80, blank=True)


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
