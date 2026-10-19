from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    AnalyticsSnapshotViewSet,
    AnomalyAlertViewSet,
    CohortSummaryViewSet,
    DashboardViewSet,
    DashboardWidgetViewSet,
    ExecutiveScorecardViewSet,
    ExportSubscriptionViewSet,
    MetricDefinitionViewSet,
    OrderCycleTimeMetricViewSet,
    ReportScheduleViewSet,
    RFQConversionMetricViewSet,
    SavedReportViewSet,
    SpendCubeViewSet,
    SupplierPerformanceMetricViewSet,
)

router = DefaultRouter()
router.register("metrics", MetricDefinitionViewSet)
router.register("dashboards", DashboardViewSet)
router.register("widgets", DashboardWidgetViewSet)
router.register("reports", SavedReportViewSet)
router.register("report-schedules", ReportScheduleViewSet)
router.register("snapshots", AnalyticsSnapshotViewSet)
router.register("spend-cubes", SpendCubeViewSet)
router.register("supplier-performance", SupplierPerformanceMetricViewSet)
router.register("order-cycle-times", OrderCycleTimeMetricViewSet)
router.register("rfq-conversions", RFQConversionMetricViewSet)
router.register("cohorts", CohortSummaryViewSet)
router.register("anomaly-alerts", AnomalyAlertViewSet)
router.register("export-subscriptions", ExportSubscriptionViewSet)
router.register("executive-scorecards", ExecutiveScorecardViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
