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
    IntegrationEvent,
    InventorySyncJob,
    MappingTemplate,
    PriceSyncJob,
    RetryPolicy,
    SFTPDropbox,
    WebhookDelivery,
    WebhookEndpoint,
    WebhookSubscription,
)


@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin)
    list_display = ("name_id", "owner", "is_active")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("prefix", "client", "status")


@admin.register(RetryPolicy)
class RetryPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "max_attempts")


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("url", "client", "is_active")


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "is_active")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "status")


@admin.register(EDIPartner)
class EDIPartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "is_active")


@admin.register(EDIDocument)
class EDIDocumentAdmin(admin.ModelAdmin):
    list_display = ("partner", "document_type", "direction")


@admin.register(ERPConnector)
class ERPConnectorAdmin(admin.ModelAdmin):
    list_display = ("name", "system", "status")


@admin.register(SFTPDropbox)
class SFTPDropboxAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "path")


@admin.register(MappingTemplate)
class MappingTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "source_format", "target_format")


@admin.register(CatalogImportJob)
class CatalogImportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "source")


@admin.register(PriceSyncJob)
class PriceSyncJobAdmin(admin.ModelAdmin):
    list_display = ("connector", "status")


@admin.register(InventorySyncJob)
class InventorySyncJobAdmin(admin.ModelAdmin):
    list_display = ("connector", "status")


@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "is_active")


@admin.register(IntegrationEvent)
class IntegrationEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "source", "created_at")


@admin.register(DeadLetterRecord)
class DeadLetterRecordAdmin(admin.ModelAdmin):
    list_display = ("event_type", "status", "attempts")
