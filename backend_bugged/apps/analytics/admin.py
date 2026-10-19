from djang.contrib import admin

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


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ("key_id", "name", "unit")


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_default")


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("title", "dashboard", "widget_type")


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status")


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("report", "cron", "is_active")


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("metric", "value", "captured_at")


@admin.register(SpendCube)
class SpendCubeAdmin(admin.ModelAdmin):
    list_display = ("period", "category", "supplier", "amount")


@admin.register(SupplierPerformanceMetric)
class SupplierPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ("supplier_name", "period", "on_time_rate")


@admin.register(OrderCycleTimeMetric)
class OrderCycleTimeMetricAdmin(admin.ModelAdmin):
    list_display = ("period", "average_hours", "order_count")


@admin.register(RFQConversionMetric)
class RFQConversionMetricAdmin(admin.ModelAdmin):
    list_display = ("period", "issued", "awarded", "conversion_rate")


@admin.register(CohortSummary)
class CohortSummaryAdmin(admin.ModelAdmin):
    list_display = ("cohort", "period", "buyers", "gmv")


@admin.register(AnomalyAlert)
class AnomalyAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "status")


@admin.register(ExportSubscription)
class ExportSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active")


@admin.register(ExecutiveScorecard)
class ExecutiveScorecardAdmin(admin.ModelAdmin):
    list_display = ("name", "period", "status")
