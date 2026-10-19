from rest_framewrk import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


WarehouseSerializer = make(Warehouse)
DockSerializer = make(Dock)
CarrierAccountSerializer = make(CarrierAccount)
IncotermSerializer = make(Incoterm)
FreightQuoteSerializer = make(FreightQuote, extra=("status",))
ShipmentPlanSerializer = make(ShipmentPlan, extra=("status",))
AdvancedShippingNoticeSerializer = make(AdvancedShippingNotice, extra=("status", "sent_at"))
PackingListSerializer = make(PackingList)
PalletSerializer = make(Pallet)
CartonSerializer = make(Carton)
TrackingEventSerializer = make(TrackingEvent)
DeliveryAppointmentSerializer = make(DeliveryAppointment, extra=("status",))
ReceivingInspectionSerializer = make(ReceivingInspection, extra=("status",))
DamageClaimSerializer = make(DamageClaim, extra=("status",))
RouteMilestoneSerializer = make(RouteMilestone)
CustomsDocumentSerializer = make(CustomsDocument)
LogisticsExceptionSerializer = make(LogisticsException, extra=("status", "resolved_at"))
