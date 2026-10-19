from rest_framework import serializers

from .models import (
    AnalyticsSnapshot,
    AnomalyAlert,
    CohortSummary,
    ComparisonPeriod,
    Dashboard,
    DashboardWidget,
    ExecutiveScorecard,
    ExportJob,
    ExportSubscription,
    ForecastModel,
    ForecastProjection,
    KpiDefinition,
    MetricDefinition,
    OrderCycleTimeMetric,
    ReportBuilderDefinition,
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
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


MetricDefinitionSerializer = make(MetricDefinition)
KpiDefinitionSerializer = make(KpiDefinition)
DashboardSerializer = make(Dashboard)
DashboardWidgetSerializer = make(DashboardWidget)
SavedReportSerializer = make(SavedReport, extra=("status", "last_run_at", "last_payload"))
ReportBuilderDefinitionSerializer = make(ReportBuilderDefinition, extra=("status", "published_at"))
ExportJobSerializer = make(ExportJob, extra=("status", "owner", "file_url", "row_count", "completed_at"))
ReportScheduleSerializer = make(ReportSchedule)
AnalyticsSnapshotSerializer = make(AnalyticsSnapshot)
ComparisonPeriodSerializer = make(ComparisonPeriod, extra=("variance", "computed_at"))
ForecastModelSerializer = make(ForecastModel, extra=("status", "last_forecast_at"))
ForecastProjectionSerializer = make(ForecastProjection)
SpendCubeSerializer = make(SpendCube)
SupplierPerformanceMetricSerializer = make(SupplierPerformanceMetric)
OrderCycleTimeMetricSerializer = make(OrderCycleTimeMetric)
RFQConversionMetricSerializer = make(RFQConversionMetric)
CohortSummarySerializer = make(CohortSummary)
AnomalyAlertSerializer = make(AnomalyAlert, extra=("status", "acknowledged_at", "resolved_at"))
ExportSubscriptionSerializer = make(ExportSubscription)
ExecutiveScorecardSerializer = make(ExecutiveScorecard, extra=("status", "published_at"))


class ForecastModelDetailSerializer(ForecastModelSerializer):
    projections = ForecastProjectionSerializer(many=True, read_only=True)

    class Meta(ForecastModelSerializer.Meta):
        fields = "__all__"
        read_only_fields = ForecastModelSerializer.Meta.read_only_fields
