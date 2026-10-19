from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    APIClientSerializer,
    APIKeySerializer,
    AutomationRuleSerializer,
    CatalogImportJobSerializer,
    DeadLetterRecordSerializer,
    EDIDocumentSerializer,
    EDIPartnerSerializer,
    ERPConnectorSerializer,
    IntegrationEventSerializer,
    InventorySyncJobSerializer,
    MappingTemplateSerializer,
    PriceSyncJobSerializer,
    RetryPolicySerializer,
    SFTPDropboxSerializer,
    WebhookDeliverySerializer,
    WebhookEndpointSerializer,
    WebhookSubscriptionSerializer,
)


def wrap_service(fn, *args, **kwargs)
    try:
        return fn(*args, **kwargs
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class APIClientViewSet(AuthenticatedViewSet):
    serializer_class = APIClientSerializer

    def get_queryset(self):
        qs = APIClient.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["post"], url_path="create-key")
    def create_key(self, request, pk=None):
        key, raw = wrap_service(services.create_api_key, self.get_object())
        payload = APIKeySerializer(key).data
        payload["secret"] = raw
        return Response(payload, status=status.HTTP_201_CREATED)


class APIKeyViewSet(AuthenticatedViewSet):
    queryset = APIKey.objects.select_related("client")
    serializer_class = APIKeySerializer

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        key = wrap_service(services.revoke_api_key, self.get_object())
        return Response(self.get_serializer(key).data)


class RetryPolicyViewSet(AuthenticatedViewSet):
    queryset = RetryPolicy.objects.all()
    serializer_class = RetryPolicySerializer


class WebhookEndpointViewSet(AuthenticatedViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer

    @action(detail=True, methods=["post"], url_path="emit-test")
    def emit_test(self, request, pk=None):
        delivery = wrap_service(services.emit_test_webhook, self.get_object(), request.data.get("event_type", "test.ping"))
        return Response(WebhookDeliverySerializer(delivery).data, status=status.HTTP_201_CREATED)


class WebhookSubscriptionViewSet(AuthenticatedViewSet):
    queryset = WebhookSubscription.objects.all()
    serializer_class = WebhookSubscriptionSerializer


class WebhookDeliveryViewSet(AuthenticatedViewSet):
    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        delivery = wrap_service(services.retry_delivery, self.get_object())
        return Response(self.get_serializer(delivery).data)


class EDIPartnerViewSet(AuthenticatedViewSet):
    queryset = EDIPartner.objects.all()
    serializer_class = EDIPartnerSerializer


class EDIDocumentViewSet(AuthenticatedViewSet):
    queryset = EDIDocument.objects.all()
    serializer_class = EDIDocumentSerializer


class ERPConnectorViewSet(AuthenticatedViewSet):
    queryset = ERPConnector.objects.all()
    serializer_class = ERPConnectorSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="queue-price-sync")
    def queue_price_sync(self, request, pk=None):
        job = wrap_service(services.queue_price_sync, self.get_object())
        return Response(PriceSyncJobSerializer(job).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="queue-inventory-sync")
    def queue_inventory_sync(self, request, pk=None):
        job = wrap_service(services.queue_inventory_sync, self.get_object())
        return Response(InventorySyncJobSerializer(job).data, status=status.HTTP_201_CREATED)


class SFTPDropboxViewSet(AuthenticatedViewSet):
    queryset = SFTPDropbox.objects.all()
    serializer_class = SFTPDropboxSerializer


class MappingTemplateViewSet(AuthenticatedViewSet):
    queryset = MappingTemplate.objects.all()
    serializer_class = MappingTemplateSerializer


class CatalogImportJobViewSet(AuthenticatedViewSet):
    queryset = CatalogImportJob.objects.all()
    serializer_class = CatalogImportJobSerializer

    @action(detail=True, methods=["post"])
    def queue(self, request, pk=None):
        job = wrap_service(services.queue_catalog_import, job=self.get_object())
        return Response(self.get_serializer(job).data)


class PriceSyncJobViewSet(AuthenticatedViewSet):
    queryset = PriceSyncJob.objects.all()
    serializer_class = PriceSyncJobSerializer


class InventorySyncJobViewSet(AuthenticatedViewSet):
    queryset = InventorySyncJob.objects.all()
    serializer_class = InventorySyncJobSerializer


class AutomationRuleViewSet(AuthenticatedViewSet):
    queryset = AutomationRule.objects.all()
    serializer_class = AutomationRuleSerializer


class IntegrationEventViewSet(AuthenticatedViewSet):
    queryset = IntegrationEvent.objects.all()
    serializer_class = IntegrationEventSerializer

    @action(detail=False, methods=["post"])
    def emit(self, request):
        event = wrap_service(
            services.emit_event,
            request.data.get("event_type", ""),
            payload=request.data.get("payload") or {},
            source=request.data.get("source", ""),
        )
        return Response(self.get_serializer(event).data, status=status.HTTP_201_CREATED)


class DeadLetterRecordViewSet(AuthenticatedViewSet):
    queryset = DeadLetterRecord.objects.all()
    serializer_class = DeadLetterRecordSerializer

    @action(detail=True, methods=["post"])
    def redrive(self, request, pk=None):
        record = wrap_service(services.redrive_dead_letter, self.get_object())
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        record = wrap_service(services.resolve_dead_letter, self.get_object(), request.data.get("note", ""))
        return Response(self.get_serializer(record).data)
