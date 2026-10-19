from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    AdvancedShippingNoticeViewSet,
    CarrierAccountViewSet,
    CartonViewSet,
    CustomsDocumentViewSet,
    DamageClaimViewSet,
    DeliveryAppointmentViewSet,
    DockViewSet,
    FreightQuoteViewSet,
    IncotermViewSet,
    LogisticsExceptionViewSet,
    PackingListViewSet,
    PalletViewSet,
    ReceivingInspectionViewSet,
    RouteMilestoneViewSet,
    ShipmentPlanViewSet,
    TrackingEventViewSet,
    WarehouseViewSet,
)

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet)
router.register("docks", DockViewSet)
router.register("carrier-accounts", CarrierAccountViewSet)
router.register("incoterms", IncotermViewSet)
router.register("freight-quotes", FreightQuoteViewSet)
router.register("shipment-plans", ShipmentPlanViewSet)
router.register("advanced-shipping-notices", AdvancedShippingNoticeViewSet)
router.register("packing-lists", PackingListViewSet)
router.register("pallets", PalletViewSet)
router.register("cartons", CartonViewSet)
router.register("tracking-events", TrackingEventViewSet)
router.register("delivery-appointments", DeliveryAppointmentViewSet)
router.register("receiving-inspections", ReceivingInspectionViewSet)
router.register("damage-claims", DamageClaimViewSet)
router.register("route-milestones", RouteMilestoneViewSet)
router.register("customs-documents", CustomsDocumentViewSet)
router.register("exceptions", LogisticsExceptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
