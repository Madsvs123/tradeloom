from rest_framework import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


WarehouseSerializer = make(Warehouse)
WarehouseZoneSerializer = make(WarehouseZone)
WarehouseBinSerializer = make(WarehouseBin)
DockSerializer = make(Dock)
CarrierAccountSerializer = make(CarrierAccount)
RateTableSerializer = make(RateTable, extra=("status",))
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
InventoryCountSerializer = make(InventoryCount, extra=("number", "status", "counted_at", "reconciled_at"))
ShipmentDocumentSerializer = make(ShipmentDocument, extra=("status", "verified_by", "verified_at"))
HazardousDeclarationSerializer = make(HazardousDeclaration, extra=("status", "decided_by", "decided_at"))
DamageClaimSerializer = make(DamageClaim, extra=("status",))
RouteMilestoneSerializer = make(RouteMilestone)
CustomsDocumentSerializer = make(CustomsDocument)
LogisticsExceptionSerializer = make(LogisticsException, extra=("status", "resolved_at"))
