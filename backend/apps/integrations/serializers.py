from rest_framework import serializers

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


class OAuthApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthApplication
        fields = "__all__"
        read_only_fields = ("id", "client_id", "client_secret", "status", "revoked_at", "created_at", "updated_at")


OAuthGrantSerializer = make(OAuthGrant, extra=("access_token", "refresh_token", "revoked_at"))
IntegrationHealthCheckSerializer = make(IntegrationHealthCheck, extra=("checked_at",))
PayloadSchemaSerializer = make(PayloadSchema)
FieldMappingSerializer = make(FieldMapping)
IntegrationAuditLogSerializer = make(IntegrationAuditLog, extra=("actor",))
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


class MappingTemplateDetailSerializer(MappingTemplateSerializer):
    field_mappings = FieldMappingSerializer(many=True, read_only=True)

    class Meta(MappingTemplateSerializer.Meta):
        fields = "__all__"
        read_only_fields = MappingTemplateSerializer.Meta.read_only_fields
