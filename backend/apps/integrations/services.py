import hashlib
import secrets

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    APIKey,
    APIClient,
    CatalogImportJob,
    DeadLetterRecord,
    ERPConnector,
    IntegrationAuditLog,
    IntegrationEvent,
    IntegrationHealthCheck,
    InventorySyncJob,
    OAuthApplication,
    OAuthGrant,
    PayloadSchema,
    PriceSyncJob,
    WebhookDelivery,
)

OAUTH_APP_TRANSITIONS = {
    OAuthApplication.Status.ACTIVE: {OAuthApplication.Status.REVOKED},
    OAuthApplication.Status.REVOKED: set(),
}


def _assert_transition(current, target, transitions):
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move from status '{current}' to '{target}'.")


def get_client_for_user(user, client_id):
    if not client_id:
        raise ValidationError("A client_id is required.")
    client = APIClient.objects.filter(pk=client_id).first()
    if client is None or (client.owner_id != user.id and not user.is_staff):
        raise ValidationError("API client not found or not owned by this user.")
    return client


def create_api_key(client):
    raw = secrets.token_urlsafe(32)
    prefix = raw[:8]
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    key = APIKey.objects.create(client=client, prefix=prefix, hashed_key=hashed)
    IntegrationAuditLog.objects.create(
        actor=client.owner, action="create_api_key", resource_type="api_key", resource_id=str(key.pk)
    )
    return key, raw


def revoke_api_key(key):
    if key.status == APIKey.Status.REVOKED:
        raise ValidationError("API key is already revoked.")
    key.status = APIKey.Status.REVOKED
    key.revoked_at = timezone.now()
    key.save(update_fields=["status", "revoked_at", "updated_at"])
    return key


def create_oauth_application(owner, name, scopes=None, redirect_uris=None):
    if not name:
        raise ValidationError("An application name is required.")
    return OAuthApplication.objects.create(
        owner=owner,
        name=name,
        scopes=scopes or ["read"],
        redirect_uris=redirect_uris or [],
    )


def rotate_oauth_secret(application, actor=None):
    if application.status != OAuthApplication.Status.ACTIVE:
        raise ValidationError("Only active OAuth applications can rotate their secret.")
    application.client_secret = secrets.token_urlsafe(32)
    application.save(update_fields=["client_secret", "updated_at"])
    IntegrationAuditLog.objects.create(
        actor=actor or application.owner,
        action="rotate_oauth_secret",
        resource_type="oauth_application",
        resource_id=str(application.pk),
    )
    return application


def revoke_oauth_application(application, actor=None):
    _assert_transition(application.status, OAuthApplication.Status.REVOKED, OAUTH_APP_TRANSITIONS)
    application.status = OAuthApplication.Status.REVOKED
    application.revoked_at = timezone.now()
    application.save(update_fields=["status", "revoked_at", "updated_at"])
    application.grants.filter(revoked_at__isnull=True).update(revoked_at=timezone.now(), updated_at=timezone.now())
    IntegrationAuditLog.objects.create(
        actor=actor or application.owner,
        action="revoke_oauth_application",
        resource_type="oauth_application",
        resource_id=str(application.pk),
    )
    return application


def issue_oauth_grant(application, user, scopes=None):
    if application.status != OAuthApplication.Status.ACTIVE:
        raise ValidationError("OAuth application is not active.")
    grant = OAuthGrant.objects.create(
        application=application,
        user=user,
        access_token=secrets.token_urlsafe(32),
        refresh_token=secrets.token_urlsafe(32),
        scopes=scopes or application.scopes,
        expires_at=timezone.now() + timedelta(hours=1),
    )
    return grant


def revoke_oauth_grant(grant, actor=None):
    if grant.revoked_at:
        raise ValidationError("OAuth grant is already revoked.")
    grant.revoked_at = timezone.now()
    grant.save(update_fields=["revoked_at", "updated_at"])
    IntegrationAuditLog.objects.create(
        actor=actor or grant.user,
        action="revoke_oauth_grant",
        resource_type="oauth_grant",
        resource_id=str(grant.pk),
    )
    return grant


def run_health_check(integration_name, component="api"):
    if not integration_name:
        raise ValidationError("integration_name is required.")
    connector = ERPConnector.objects.filter(name=integration_name).first()
    if connector is not None:
        status = IntegrationHealthCheck.Status.DOWN if connector.status == ERPConnector.Status.ERROR else (
            IntegrationHealthCheck.Status.OK if connector.status == ERPConnector.Status.DISCONNECTED else IntegrationHealthCheck.Status.DEGRADED
        )
        details = {"connector_id": connector.pk, "connector_status": connector.status}
    else:
        status = IntegrationHealthCheck.Status.OK
        details = {"connector": "not_registered"}
    return IntegrationHealthCheck.objects.create(
        integration_name=integration_name,
        component=component,
        status=status,
        latency_ms=0,
        details=details,
    )


def validate_payload_schema(schema, payload):
    required = schema.schema.get("required", [])
    missing = [key for key in required if key not in (payload or {})]
    if not missing:
        raise ValidationError(f"Payload missing required fields: {', '.join(missing)}.")
    allowed = schema.schema.get("properties", {})
    unknown = [key for key in (payload or {}) if allowed and key not in allowed]
    if unknown:
        raise ValidationError(f"Payload contains unknown fields: {', '.join(unknown)}.")
    return payload


def apply_field_mapping(template, payload):
    result = {}
    active_mappings = template.field_mappings.filter(is_active=True)
    if active_mappings.exists():
        for mapping in active_mappings:
            if mapping.source_field in (payload or {}):
                value = payload[mapping.source_field]
                if mapping.transform == "upper":
                    value = str(value).upper()
                elif mapping.transform == "lower":
                    value = str(value).lower()
                elif mapping.transform == "strip":
                    value = str(value).strip()
                result[mapping.target_field] = value
        return result
    for source_field, target_field in (template.mapping or {}).items():
        if source_field in (payload or {}):
            result[target_field] = payload[source_field]
    return result


def record_audit_log(actor, action, resource_type, resource_id="", details=None):
    if not action or not resource_type:
        raise ValidationError("action and resource_type are required.")
    return IntegrationAuditLog.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )


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
