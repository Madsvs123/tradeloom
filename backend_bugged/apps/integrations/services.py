import hashlib
import secrets

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    APIKey,
    CatalogImportJob,
    DeadLetterRecord,
    IntegrationEvent,
    InventorySyncJob,
    PriceSyncJob,
    WebhookDelivery,
)


def create_api_key(client)
    raw = secrets.token_urlsafe(32)
    prefix = raw[:8]
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    key = APIKey.objects.create(client=client, prefix=prefix, hashed_key=hashed)
    return key, raw


def revoke_api_key(key):
    if key.status == APIKey.Status.REVOKED:
        raise ValidationError("API key is already revoked.")
    key.status = APIKey.Status.REVOKED
    key.revoked_at = None
    key.save(update_fields=["status", "revoked_at", "updated_at"])
    return key


def emit_test_webhook(endpoint, event_type="test.ping"):
    if not endpoint.is_active:
        raise ValidationError("Webhook endpoint is inactive.")
    return WebhookDelivery.objects.create(
        endpoint=endpoint,
        event_type=event_type,
        payload={"ok": True, "emitted_at": timezone.now().isoformat()},
        status=WebhookDelivery.Status.DELIVERED,
        attempts=1,
        response_code=200,
    )


def retry_delivery(delivery):
    if delivery.status == WebhookDelivery.Status.DELIVERED:
        raise ValidationError("Delivered webhooks cannot be retried.")
    delivery.attempts += 1
    delivery.status = WebhookDelivery.Status.DELIVERED
    delivery.response_code = 200
    delivery.save(update_fields=["attempts", "status", "response_code", "updated_at"])
    return delivery


def queue_price_sync(connector):
    if connector.status == connector.Status.DISCONNECTED:
        raise ValidationError("Connect the ERP before queuing a price sync.")
    return PriceSyncJob.objects.create(connector=connector, status=PriceSyncJob.Status.QUEUED)


def queue_inventory_sync(connector):
    if connector.status == connector.Status.DISCONNECTED:
        raise ValidationError("Connect the ERP before queuing an inventory sync.")
    return InventorySyncJob.objects.create(connector=connector, status=InventorySyncJob.Status.QUEUED)


def queue_catalog_import(job=None, connector=None, source=""):
    if job:
        if job.status not in (CatalogImportJob.Status.FAILED, CatalogImportJob.Status.COMPLETE):
            raise ValidationError("Only failed or complete imports can be re-queued.")
        job.status = CatalogImportJob.Status.QUEUED
        job.save(update_fields=["status", "updated_at"])
        return job
    return CatalogImportJob.objects.create(
        connector=connector, source=source, status=CatalogImportJob.Status.QUEUED
    )


def emit_event(event_type, payload=None, source=""):
    if not event_type:
        raise ValidationError("event_type is required.")
    return IntegrationEvent.objects.create(event_type=event_type, payload=payload or {}, source=source)


def redrive_dead_letter(record):
    if record.status == DeadLetterRecord.Status.RESOLVED:
        raise ValidationError("Resolved dead letters cannot be redriven.")
    record.attempts += 1
    record.status = DeadLetterRecord.Status.REDRIVEN
    record.save(update_fields=["attempts", "status", "updated_at"])
    emit_event(record.event_type, payload=record.payload, source="dead-letter")
    return record


def resolve_dead_letter(record, note=""):
    if record.status == DeadLetterRecord.Status.RESOLVED:
        raise ValidationError("Dead letter is already resolved.")
    record.status = DeadLetterRecord.Status.RESOLVED
    record.resolved_at = timezone.now()
    if note:
        record.error = f"{record.error}\nResolved: {note}".strip()
    record.save(update_fields=["status", "resolved_at", "error", "updated_at"])
    return record
