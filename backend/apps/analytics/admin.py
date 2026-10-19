from django.contrib import admin

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


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "unit")
    search_fields = ("key", "name")


@admin.register(KpiDefinition)
class KpiDefinitionAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "formula", "unit", "direction", "target_value", "is_active")
    list_filter = ("direction", "is_active")


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_default")
    list_filter = ("is_default",)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("title", "dashboard", "widget_type", "position")


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "last_run_at")
    list_filter = ("status",)


@admin.register(ReportBuilderDefinition)
class ReportBuilderDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "source", "status", "published_at")
    list_filter = ("status", "source")


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ("owner", "report", "export_format", "status", "row_count", "completed_at")
    list_filter = ("status", "export_format")


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("report", "cron", "is_active")


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("metric", "value", "captured_at")


@admin.register(ComparisonPeriod)
class ComparisonPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "base_period", "comparison_period", "computed_at")


@admin.register(ForecastModel)
class ForecastModelAdmin(admin.ModelAdmin):
    list_display = ("name", "metric", "algorithm", "horizon_days", "status", "last_forecast_at")
    list_filter = ("status", "algorithm")


@admin.register(ForecastProjection)
class ForecastProjectionAdmin(admin.ModelAdmin):
    list_display = ("model", "period", "predicted_value", "actual_value")


@admin.register(SpendCube)
class SpendCubeAdmin(admin.ModelAdmin):
    list_display = ("period", "category", "supplier", "amount", "currency")
    list_filter = ("period", "currency")


@admin.register(SupplierPerformanceMetric)
class SupplierPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ("supplier_name", "period", "on_time_rate", "quality_rate", "spend")


@admin.register(OrderCycleTimeMetric)
class OrderCycleTimeMetricAdmin(admin.ModelAdmin):
    list_display = ("period", "average_hours", "median_hours", "order_count")


@admin.register(RFQConversionMetric)
class RFQConversionMetricAdmin(admin.ModelAdmin):
    list_display = ("period", "issued", "awarded", "conversion_rate")


@admin.register(CohortSummary)
class CohortSummaryAdmin(admin.ModelAdmin):
    list_display = ("cohort", "period", "buyers", "gmv")


@admin.register(AnomalyAlert)
class AnomalyAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "metric", "severity", "status", "acknowledged_at", "resolved_at")
    list_filter = ("status", "severity")


@admin.register(ExportSubscription)
class ExportSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "destination", "is_active")


@admin.register(ExecutiveScorecard)
class ExecutiveScorecardAdmin(admin.ModelAdmin):
    list_display = ("name", "period", "status", "published_at")
    list_filter = ("status",)
