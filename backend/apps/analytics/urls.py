from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsSnapshotViewSet,
    AnomalyAlertViewSet,
    CohortSummaryViewSet,
    ComparisonPeriodViewSet,
    DashboardViewSet,
    DashboardWidgetViewSet,
    ExecutiveScorecardViewSet,
    ExportJobViewSet,
    ExportSubscriptionViewSet,
    ForecastModelViewSet,
    ForecastProjectionViewSet,
    KpiDefinitionViewSet,
    MetricDefinitionViewSet,
    OrderCycleTimeMetricViewSet,
    ReportBuilderDefinitionViewSet,
    ReportScheduleViewSet,
    RFQConversionMetricViewSet,
    SavedReportViewSet,
    SpendCubeViewSet,
    SupplierPerformanceMetricViewSet,
)

router = DefaultRouter()
router.register("metrics", MetricDefinitionViewSet)
router.register("kpis", KpiDefinitionViewSet)
router.register("dashboards", DashboardViewSet)
router.register("widgets", DashboardWidgetViewSet)
router.register("reports", SavedReportViewSet)
router.register("report-builders", ReportBuilderDefinitionViewSet)
router.register("export-jobs", ExportJobViewSet)
router.register("reports", SavedReportViewSet)
router.register("report-schedules", ReportScheduleViewSet)
router.register("snapshots", AnalyticsSnapshotViewSet)
router.register("comparison-periods", ComparisonPeriodViewSet)
router.register("forecast-models", ForecastModelViewSet)
router.register("forecast-projections", ForecastProjectionViewSet)
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
