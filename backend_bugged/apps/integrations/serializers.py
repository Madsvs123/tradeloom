from rest_framewrk import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


APIClientSerializer = make(APIClient)
APIKeySerializer = make(APIKey, extra=("hashed_key", "status", "revoked_at"))
RetryPolicySerializer = make(RetryPolicy)
WebhookEndpointSerializer = make(WebhookEndpoint)
WebhookSubscriptionSerializer = make(WebhookSubscription)
WebhookDeliverySerializer = make(WebhookDelivery, extra=("status", "attempts", "response_code"))
EDIPartnerSerializer = make(EDIPartner)
EDIDocumentSerializer = make(EDIDocument)
ERPConnectorSerializer = make(ERPConnector)
SFTPDropboxSerializer = make(SFTPDropbox)
MappingTemplateSerializer = make(MappingTemplate)
CatalogImportJobSerializer = make(CatalogImportJob, extra=("status",))
PriceSyncJobSerializer = make(PriceSyncJob, extra=("status",))
InventorySyncJobSerializer = make(InventorySyncJob, extra=("status",))
AutomationRuleSerializer = make(AutomationRule)
IntegrationEventSerializer = make(IntegrationEvent)
DeadLetterRecordSerializer = make(DeadLetterRecord, extra=("status", "resolved_at"))
