from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerRelationshipNoteViewSet,
    DisputeDashboardView,
    DisputeViewSet,
    IncomingOrderViewSet,
    IncomingWorkDashboardView,
    InventoryAdjustmentViewSet,
    InventoryDashboardView,
    InventoryItemViewSet,
    PayoutDashboardView,
    PayoutViewSet,
    PriceBookChangeViewSet,
    PriceBookItemViewSet,
    PriceChangeRequestViewSet,
    RFQViewSet,
    SalesAnalyticsView,
    ServiceRatingViewSet,
    VendorAccountViewSet,
    VendorAnnouncementViewSet,
    VendorDocumentViewSet,
    VendorPerformanceRecordViewSet,
    VendorReportViewSet,
    VendorScorecardViewSet,
    VendorTeamMembershipViewSet,
)

app_name = "vendor_ops"

router = DefaultRouter()
router.register("vendors", VendorAccountViewSet, basename="vendor")
router.register("team-memberships", VendorTeamMembershipViewSet, basename="vendor")
router.register("performance-records", VendorPerformanceRecordViewSet, basename="performance-record")
router.register("scorecards", VendorScorecardViewSet, basename="scorecard")
router.register("vendor-documents", VendorDocumentViewSet, basename="vendor-document")
router.register("price-change-requests", PriceChangeRequestViewSet, basename="price-change-request")
router.register("announcements", VendorAnnouncementViewSet, basename="announcement")
router.register("service-ratings", ServiceRatingViewSet, basename="service-rating")
router.register("inventory/items", InventoryItemViewSet, basename="inventory-item")
router.register("inventory/adjustments", InventoryAdjustmentViewSet, basename="inventory-adjustment")
router.register("price-book/items", PriceBookItemViewSet, basename="price-book-item")
router.register("price-book/changes", PriceBookChangeViewSet, basename="price-book-change")
router.register("orders", IncomingOrderViewSet, basename="incoming-order")
router.register("rfqs", RFQViewSet, basename="rfq")
router.register("customer-notes", CustomerRelationshipNoteViewSet, basename="customer-note")
router.register("payouts", PayoutViewSet, basename="payout")
router.register("disputes", DisputeViewSet, basename="dispute")
router.register("reports", VendorReportViewSet, basename="report")

urlpatterns = [
    path("v2/", include(router.urls)),
    path("dashboards/incoming-work/", IncomingWorkDashboardView.as_view(), name="incoming-work-dashboard"),
    path("dashboards/inventory/", InventoryDashboardView.as_view(), name="inventory-dashboard"),
    path("dashboards/payouts/", PayoutDashboardView.as_view(), name="payout-dashboard"),
    path("dashboards/disputes/", DisputeDashboardView.as_view(), name="dispute-dashboard"),
    path("analytics/sales/", SalesAnalyticsView.as_view(), name="sales-analytics"),
]
