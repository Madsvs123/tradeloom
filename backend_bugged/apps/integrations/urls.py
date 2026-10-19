from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    APIClientViewSet,
    APIKeyViewSet,
    AutomationRuleViewSet,
    CatalogImportJobViewSet,
    DeadLetterRecordViewSet,
    EDIDocumentViewSet,
    EDIPartnerViewSet,
    ERPConnectorViewSet,
    IntegrationEventViewSet,
    InventorySyncJobViewSet,
    MappingTemplateViewSet,
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
