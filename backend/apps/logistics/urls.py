from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdvancedShippingNoticeViewSet,
    CarrierAccountViewSet,
    CartonViewSet,
    CustomsDocumentViewSet,
    DamageClaimViewSet,
    DeliveryAppointmentViewSet,
    DockViewSet,
    FreightQuoteViewSet,
    HazardousDeclarationViewSet,
    IncotermViewSet,
    InventoryCountViewSet,
    LogisticsExceptionViewSet,
    PackingListViewSet,
    PalletViewSet,
    RateTableViewSet,
    ReceivingInspectionViewSet,
    RouteMilestoneViewSet,
    ShipmentDocumentViewSet,
    ShipmentPlanViewSet,
    TrackingEventViewSet,
    WarehouseBinViewSet,
    WarehouseViewSet,
    WarehouseZoneViewSet,
)

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet)
router.register("warehouse-zones", WarehouseZoneViewSet)
router.register("warehouse-bins", WarehouseBinViewSet)
router.register("docks", DockViewSet)
router.register("carrier-accounts", CarrierAccountViewSet)
router.register("rate-tables", RateTableViewSet)
router.register("incoterms", IncotermViewSet)
router.register("freight-quotes", FreightQuoteViewSet)
router.register("shipment-plans", ShipmentPlanViewSet)
router.register("advanced-shipping-notices", AdvancedShippingNoticeViewSet)
router.register("packing-lists", PackingListViewSet)
router.register("pallets", PalletViewSet)
router.register("cartons", CartonViewSet)
router.register("cartons", CartonViewSet)
router.register("tracking-events", TrackingEventViewSet)
router.register("delivery-appointments", DeliveryAppointmentViewSet)
router.register("receiving-inspections", ReceivingInspectionViewSet)
router.register("inventory-counts", InventoryCountViewSet)
router.register("shipment-documents", ShipmentDocumentViewSet)
router.register("hazardous-declarations", HazardousDeclarationViewSet)
router.register("damage-claims", DamageClaimViewSet)
router.register("route-milestones", RouteMilestoneViewSet)
router.register("customs-documents", CustomsDocumentViewSet)
router.register("exceptions", LogisticsExceptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
