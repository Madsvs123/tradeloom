from django.contrib import admin

from .models import (
    APIClient,
    APIKey,
    AutomationRule,
    CatalogImportJob,
    DeadLetterRecord,
    EDIDocument,
    EDIPartner,
    ERPConnector,
    FieldMapping,
    IntegrationAuditLog,
    IntegrationEvent,
    IntegrationHealthCheck,
    InventorySyncJob,
    MappingTemplate,
    OAuthApplication,
    OAuthGrant,
    PayloadSchema,
    PriceSyncJob,
    RetryPolicy,
    SFTPDropbox,
    WebhookDelivery,
    WebhookEndpoint,
    WebhookSubscription,
)


class FieldMappingInline(admin.TabularInline):
    model = FieldMapping
    extra = 0


@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("prefix", "client", "status", "last_used_at", "revoked_at")
    list_filter = ("status",)


@admin.register(OAuthApplication)
class OAuthApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "client_id", "status", "revoked_at")
    list_filter = ("status",)
    search_fields = ("name", "client_id")


@admin.register(OAuthGrant)
class OAuthGrantAdmin(admin.ModelAdmin):
    list_display = ("application", "user", "expires_at", "revoked_at")
    list_filter = ("application",)


@admin.register(IntegrationHealthCheck)
class IntegrationHealthCheckAdmin(admin.ModelAdmin):
    list_display = ("integration_name", "component", "status", "latency_ms", "checked_at")
    list_filter = ("status", "integration_name")


@admin.register(PayloadSchema)
class PayloadSchemaAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "version", "is_active")
    list_filter = ("is_active",)


@admin.register(FieldMapping)
class FieldMappingAdmin(admin.ModelAdmin):
    list_display = ("template", "source_field", "target_field", "transform", "is_active")
    list_filter = ("is_active",)


@admin.register(IntegrationAuditLog)
class IntegrationAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "resource_type", "resource_id", "actor", "created_at")
    list_filter = ("action", "resource_type")
    search_fields = ("resource_type", "resource_id")


@admin.register(RetryPolicy)
class RetryPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "max_attempts", "backoff_seconds")


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("url", "client", "is_active")
    list_filter = ("is_active",)


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "is_active")
    list_filter = ("is_active",)


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "status", "attempts", "response_code", "created_at")
    list_filter = ("status",)


@admin.register(EDIPartner)
class EDIPartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "qualifier", "identifier", "is_active")
    list_filter = ("is_active",)


@admin.register(EDIDocument)
class EDIDocumentAdmin(admin.ModelAdmin):
    list_display = ("partner", "document_type", "direction", "reference")
    list_filter = ("direction", "document_type")


@admin.register(ERPConnector)
class ERPConnectorAdmin(admin.ModelAdmin):
    list_display = ("name", "system", "owner", "status")
    list_filter = ("status", "system")


@admin.register(SFTPDropbox)
class SFTPDropboxAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "path", "is_active")
    list_filter = ("is_active",)


@admin.register(MappingTemplate)
class MappingTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "source_format", "target_format")
    inlines = (FieldMappingInline,)


@admin.register(CatalogImportJob)
class CatalogImportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "connector", "status", "source", "created_at")
    list_filter = ("status",)


@admin.register(PriceSyncJob)
class PriceSyncJobAdmin(admin.ModelAdmin):
    list_display = ("connector", "status", "created_at")
    list_filter = ("status",)


@admin.register(InventorySyncJob)
class InventorySyncJobAdmin(admin.ModelAdmin):
    list_display = ("connector", "status", "created_at")
    list_filter = ("status",)


@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "action", "is_active")
    list_filter = ("is_active",)


@admin.register(IntegrationEvent)
class IntegrationEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "source", "created_at")
    list_filter = ("event_type",)


@admin.register(DeadLetterRecord)
class DeadLetterRecordAdmin(admin.ModelAdmin):
    list_display = ("event_type", "status", "attempts", "created_at")
    list_filter = ("status",)
