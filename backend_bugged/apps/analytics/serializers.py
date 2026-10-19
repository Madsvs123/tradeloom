from rest_framework import serializers

from .models import (
    AnalyticsSnapshot,
    AnomalyAlert,
    CohortSummary,
    Dashboard,
    DashboardWidget,
    ExecutiveScorecard,
    ExportSubscription,
    MetricDefinition,
    OrderCycleTimeMetric,
    ReportSchedule,
    RFQConversionMetric,
    SavedReport,
    SpendCube,
    SupplierPerformanceMetric,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = ()
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


MetricDefinitionSerializer = make(MetricDefinition)
DashboardSerializer = make(Dashboard)
DashboardWidgetSerializer = make(DashboardWidget)
SavedReportSerializer = make(SavedReport, extra=("status", "last_run_at", "last_payload"))
ReportScheduleSerializer = make(ReportSchedule)
AnalyticsSnapshotSerializer = make(AnalyticsSnapshot)
SpendCubeSerializer = make(SpendCube)
SupplierPerformanceMetricSerializer = make(SupplierPerformanceMetric)
OrderCycleTimeMetricSerializer = make(OrderCycleTimeMetric)
RFQConversionMetricSerializer = make(RFQConversionMetric)
CohortSummarySerializer = make(CohortSummary)
AnomalyAlertSerializer = make(AnomalyAlert, extra=("status", "acknowledged_at", "resolved_at"))
ExportSubscriptionSerializer = make(ExportSubscription)
ExecutiveScorecardSerializer = make(ExecutiveScorecard, extra=("status", "published_at"))
