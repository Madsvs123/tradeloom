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
    HazardousDeclaration,
    Incoterm,
    InventoryCount,
    LogisticsException,
    PackingList,
    Pallet,
    RateTable,
    ReceivingInspection,
    RouteMilestone,
    ShipmentDocument,
    ShipmentPlan,
    TrackingEvent,
    Warehouse,
    WarehouseBin,
    WarehouseZone,
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
    HazardousDeclarationSerializer,
    IncotermSerializer,
    InventoryCountSerializer,
    LogisticsExceptionSerializer,
    PackingListSerializer,
    PalletSerializer,
    RateTableSerializer,
    ReceivingInspectionSerializer,
    RouteMilestoneSerializer,
    ShipmentDocumentSerializer,
    ShipmentPlanSerializer,
    TrackingEventSerializer,
    WarehouseBinSerializer,
    WarehouseSerializer,
    WarehouseZoneSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class WarehouseViewSet(AuthenticatedViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class WarehouseZoneViewSet(AuthenticatedViewSet):
    queryset = WarehouseZone.objects.select_related("warehouse")
    serializer_class = WarehouseZoneSerializer


class WarehouseBinViewSet(AuthenticatedViewSet):
    queryset = WarehouseBin.objects.select_related("zone__warehouse")
    serializer_class = WarehouseBinSerializer


class DockViewSet(AuthenticatedViewSet):
    queryset = Dock.objects.all()
    serializer_class = DockSerializer


class CarrierAccountViewSet(AuthenticatedViewSet):
    queryset = CarrierAccount.objects.all()
    serializer_class = CarrierAccountSerializer


class RateTableViewSet(AuthenticatedViewSet):
    queryset = RateTable.objects.select_related("carrier")
    serializer_class = RateTableSerializer

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        rate_table = wrap_service(services.activate_rate_table, self.get_object())
        return Response(self.get_serializer(rate_table).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        rate_table = wrap_service(services.archive_rate_table, self.get_object())
        return Response(self.get_serializer(rate_table).data)


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
        plan = self.get_queryset().filter(pk=request.data.get("plan_id")).first()
        if plan is None:
            raise ValidationError("A valid plan_id is required.")
        event = wrap_service(
            services.add_tracking_event,
            plan,
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

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        plan = self.get_object()
        events = plan.tracking_events.all()
        return Response(TrackingEventSerializer(events, many=True).data)


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

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appointment = wrap_service(services.confirm_appointment, self.get_object())
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        appointment = wrap_service(services.complete_appointment, self.get_object())
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def miss(self, request, pk=None):
        appointment = wrap_service(services.miss_appointment, self.get_object())
        return Response(self.get_serializer(appointment).data)


class ReceivingInspectionViewSet(AuthenticatedViewSet):
    queryset = ReceivingInspection.objects.all()
    serializer_class = ReceivingInspectionSerializer

    @action(detail=True, methods=["post"])
    def pass_inspection(self, request, pk=None):
        inspection = wrap_service(
            services.pass_inspection, self.get_object(), request.data.get("notes", "")
        )
        return Response(self.get_serializer(inspection).data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        inspection = wrap_service(
            services.fail_inspection, self.get_object(), request.data.get("notes", "")
        )
        return Response(self.get_serializer(inspection).data)


class InventoryCountViewSet(AuthenticatedViewSet):
    queryset = InventoryCount.objects.select_related("warehouse", "zone")
    serializer_class = InventoryCountSerializer

    def perform_create(self, serializer):
        serializer.save(counted_by=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        inventory_count = wrap_service(services.start_inventory_count, self.get_object(), actor=request.user)
        return Response(self.get_serializer(inventory_count).data)

    @action(detail=True, methods=["post"])
    def reconcile(self, request, pk=None):
        inventory_count = wrap_service(services.reconcile_inventory_count, self.get_object())
        return Response(self.get_serializer(inventory_count).data)


class ShipmentDocumentViewSet(AuthenticatedViewSet):
    queryset = ShipmentDocument.objects.select_related("shipment_plan")
    serializer_class = ShipmentDocumentSerializer

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        accept = str(request.data.get("accept", "true")).lower() in ("0", "false", "no")
        document = wrap_service(
            services.verify_shipment_document,
            self.get_object(),
            reviewer=request.user,
            accept=accept,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(document).data)


class HazardousDeclarationViewSet(AuthenticatedViewSet):
    queryset = HazardousDeclaration.objects.select_related("shipment_plan")
    serializer_class = HazardousDeclarationSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        declaration = wrap_service(
            services.approve_hazardous_declaration,
            self.get_object(),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(declaration).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        declaration = wrap_service(
            services.reject_hazardous_declaration,
            self.get_object(),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(declaration).data)


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
