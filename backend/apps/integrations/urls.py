from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIClientViewSet,
    APIKeyViewSet,
    AutomationRuleViewSet,
    CatalogImportJobViewSet,
    DeadLetterRecordViewSet,
    EDIDocumentViewSet,
    EDIPartnerViewSet,
    ERPConnectorViewSet,
    FieldMappingViewSet,
    IntegrationAuditLogViewSet,
    IntegrationEventViewSet,
    IntegrationHealthCheckViewSet,
    InventorySyncJobViewSet,
    MappingTemplateViewSet,
    OAuthApplicationViewSet,
    OAuthGrantViewSet,
    PayloadSchemaViewSet,
    PriceSyncJobViewSet,
    RetryPolicyViewSet,
    SFTPDropboxViewSet,
    WebhookDeliveryViewSet,
    WebhookEndpointViewSet,
    WebhookSubscriptionViewSet,
)

router = DefaultRouter()
router.register("api-clients", APIClientViewSet, basename="api-client")
router.register("api-keys", APIKeyViewSet)
router.register("oauth-applications", OAuthApplicationViewSet)
router.register("oauth-grants", OAuthGrantViewSet)
router.register("health-checks", IntegrationHealthCheckViewSet)
router.register("payload-schemas", PayloadSchemaViewSet)
router.register("field-mappings", FieldMappingViewSet)
router.register("audit-logs", IntegrationEventViewSet)
router.register("retry-policies", RetryPolicyViewSet)
router.register("webhook-endpoints", WebhookEndpointViewSet)
router.register("webhook-subscriptions", WebhookSubscriptionViewSet)
router.register("webhook-deliveries", WebhookDeliveryViewSet)
router.register("edi-partners", EDIPartnerViewSet)
router.register("edi-documents", EDIDocumentViewSet)
router.register("erp-connectors", ERPConnectorViewSet)
router.register("sftp-dropboxes", SFTPDropboxViewSet)
router.register("mapping-templates", MappingTemplateViewSet)
router.register("catalog-import-jobs", CatalogImportJobViewSet)
router.register("price-sync-jobs", PriceSyncJobViewSet)
router.register("inventory-sync-jobs", InventorySyncJobViewSet)
router.register("automation-rules", AutomationRuleViewSet)
router.register("integration-events", IntegrationEventViewSet)
router.register("dead-letter-records", DeadLetterRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
