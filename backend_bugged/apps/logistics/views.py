from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    AdvancedShippingNotice,
    CarrierAccount,
    Carton,
    CustomsDocument,
    DamageClaim,
    DeliveryAppointment,
    Dock,
    FreightQuote,
    Incoterm,
    LogisticsException,
    PackingList,
    Pallet,
    ReceivingInspection,
    RouteMilestone,
    ShipmentPlan,
    TrackingEvent,
    Warehouse,
)
from .serializers import (
    AdvancedShippingNoticeSerializer,
    CarrierAccountSerializer,
    CartonSerializer,
    CustomsDocumentSerializer,
    DamageClaimSerializer,
    DeliveryAppointmentSerializer,
    DockSerializer,
    FreightQuoteSerializer,
    IncotermSerializer,
    LogisticsExceptionSerializer,
    PackingListSerializer,
    PalletSerializer,
    ReceivingInspectionSerializer,
    RouteMilestoneSerializer,
    ShipmentPlanSerializer,
    TrackingEventSerializer,
    WarehouseSerializer,
)


def wrap_service(fn, *args, **kwargs)
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class WarehouseViewSet(AuthenticatedViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class DockViewSet(AuthenticatedViewSet):
    queryset = Dock.objects.all()
    serializer_class = DockSerializer


class CarrierAccountViewSet(AuthenticatedViewSet):
    queryset = CarrierAccount.objects.all()
    serializer_class = CarrierAccountSerializer


class IncotermViewSet(AuthenticatedViewSet):
    queryset = Incoterm.objects.all()
    serializer_class = IncotermSerializer


class FreightQuoteViewSet(AuthenticatedViewSet):
    queryset = FreightQuote.objects.all()
    serializer_class = FreightQuoteSerializer


class ShipmentPlanViewSet(AuthenticatedViewSet):
    queryset = ShipmentPlan.objects.select_related("warehouse", "carrier")
    serializer_class = ShipmentPlanSerializer

    @action(detail=False, methods=["post"], url_path="add-tracking-event")
    def add_tracking_event(self, request, pk=None):
        event = wrap_service(
            services.add_tracking_event,
            self.get_object(),
            request.data.get("status", ""),
            location=request.data.get("location", ""),
            description=request.data.get("description", ""),
        )
        return Response(TrackingEventSerializer(event).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="create-packing-list")
    def create_packing_list(self, request, pk=None):
        packing = wrap_service(
            services.create_packing_list,
            self.get_object(),
            package_count=int(request.data.get("package_count", 0) or 0),
            gross_weight_kg=request.data.get("gross_weight_kg", 0),
            notes=request.data.get("notes", ""),
        )
        return Response(PackingListSerializer(packing).data, status=status.HTTP_201_CREATED)


class AdvancedShippingNoticeViewSet(AuthenticatedViewSet):
    queryset = AdvancedShippingNotice.objects.select_related("shipment_plan")
    serializer_class = AdvancedShippingNoticeSerializer

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        asn = wrap_service(services.send_asn, self.get_object())
        return Response(self.get_serializer(asn).data)


class PackingListViewSet(AuthenticatedViewSet):
    queryset = PackingList.objects.all()
    serializer_class = PackingListSerializer


class PalletViewSet(AuthenticatedViewSet):
    queryset = Pallet.objects.all()
    serializer_class = PalletSerializer


class CartonViewSet(AuthenticatedViewSet):
    queryset = Carton.objects.all()
    serializer_class = CartonSerializer


class TrackingEventViewSet(AuthenticatedViewSet):
    queryset = TrackingEvent.objects.all()
    serializer_class = TrackingEventSerializer


class DeliveryAppointmentViewSet(AuthenticatedViewSet):
    queryset = DeliveryAppointment.objects.all()
    serializer_class = DeliveryAppointmentSerializer


class ReceivingInspectionViewSet(AuthenticatedViewSet):
    queryset = ReceivingInspection.objects.all()
    serializer_class = ReceivingInspectionSerializer


class DamageClaimViewSet(AuthenticatedViewSet):
    queryset = DamageClaim.objects.all()
    serializer_class = DamageClaimSerializer


class RouteMilestoneViewSet(AuthenticatedViewSet):
    queryset = RouteMilestone.objects.all()
    serializer_class = RouteMilestoneSerializer


class CustomsDocumentViewSet(AuthenticatedViewSet):
    queryset = CustomsDocument.objects.all()
    serializer_class = CustomsDocumentSerializer


class LogisticsExceptionViewSet(AuthenticatedViewSet):
    queryset = LogisticsException.objects.all()
    serializer_class = LogisticsExceptionSerializer

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        exception = wrap_service(services.resolve_exception, self.get_object(), request.data.get("resolution", ""))
        return Response(self.get_serializer(exception).data)
