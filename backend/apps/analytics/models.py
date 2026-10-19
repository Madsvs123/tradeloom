from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MetricDefinition(TimeStampedModel):
    key = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=40, blank=True)
    query = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.name


class KpiDefinition(TimeStampedModel):
    class Direction(models.TextChoices):
        UP = "up", "Higher is better"
        DOWN = "down", "Lower is better"

    key = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    formula = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    direction = models.CharField(max_length=16, choices=Direction.choices, default="down")
    target_value = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.name


class Dashboard(TimeStampedModel):
    name = models.CharField(max_length=160)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_dashboards")
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)


class DashboardWidget(TimeStampedModel):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    metric = models.ForeignKey(MetricDefinition, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=160)
    widget_type = models.CharField(max_length=40, default="kpi")
    position = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("dashboard", "position")


class SavedReport(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"

    name = models.CharField(max_length=80)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_reports")
    query = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-updated_at",)


class ReportBuilderDefinition(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    name = models.CharField(max_length=160)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_builder_definitions"
    )
    source = models.CharField(max_length=80, default="spend_cube")
    dimensions = models.JSONField(default=list, blank=True)
    measures = models.JSONField(default=list, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.name


class ExportJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    class Format(models.TextChoices):
        CSV = "csv", "CSV"
        XLSX = "xlsx", "XLSX"
        PDF = "pdf", "PDF"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_export_jobs")
    report = models.ForeignKey(SavedReport, null=True, blank=True, on_delete=models.SET_NULL, related_name="export_jobs")
    export_format = models.CharField(max_length=16, choices=Format.choices, default=Format.CSV)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    file_url = models.URLField(blank=True)
    row_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Export {self.pk} ({self.export_format})"


class ReportSchedule(TimeStampedModel):
    report = models.ForeignKey(SavedReport, on_delete=models.CASCADE, related_name="schedules")
    cron = models.CharField(max_length=80, default="0 8 * * 1")
    is_active = models.BooleanField(default=True)
    recipients = models.JSONField(default=list, blank=True)


class AnalyticsSnapshot(TimeStampedModel):
    metric = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE, related_name="snapshots")
    captured_at = models.DateTimeField(default=timezone.now)
    value = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    dimensions = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-captured_at",)


class ComparisonPeriod(TimeStampedModel):
    name = models.CharField(max_length=160)
    base_period = models.CharField(max_length=32)
    comparison_period = models.CharField(max_length=32)
    metric_keys = models.JSONField(default=list, blank=True)
    variance = models.JSONField(default=dict, blank=True)
    computed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="comparison_periods"
    )

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("base_period", "comparison_period")

    def __str__(self):
        return f"{self.base_period} vs {self.comparison_period}"


class ForecastModel(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        TRAINED = "trained", "Trained"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=160)
    metric = models.ForeignKey(MetricDefinition, null=True, blank=True, on_delete=models.SET_NULL, related_name="forecast_models")
    horizon_days = models.PositiveIntegerField(default=30)
    algorithm = models.CharField(max_length=80, default="linear")
    params = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="forecast_models"
    )
    last_forecast_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class ForecastProjection(TimeStampedModel):
    model = models.ForeignKey(ForecastModel, on_delete=models.CASCADE, related_name="projections")
    period = models.CharField(max_length=32)
    predicted_value = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    confidence_low = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    confidence_high = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))
    actual_value = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)

    class Meta:
        ordering = ("period",)
        unique_together = ("model", "period")

    def __str__(self):
        return f"{self.model.name} {self.period}"


class SpendCube(TimeStampedModel):
    period = models.CharField(max_length=32)
    category = models.CharField(max_length=120, blank=True)
    supplier = models.CharField(max_length=180, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        ordering = ("period", "category")


class SupplierPerformanceMetric(TimeStampedModel):
    supplier_name = models.CharField(max_length=180)
    period = models.CharField(max_length=32)
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    quality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    spend = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("period", "supplier_name")


class OrderCycleTimeMetric(TimeStampedModel):
    period = models.CharField(max_length=32)
    average_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    median_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    order_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("period",)


class RFQConversionMetric(TimeStampedModel):
    period = models.CharField(max_length=32)
    issued = models.PositiveIntegerField(default=0)
    awarded = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("period",)


class CohortSummary(TimeStampedModel):
    cohort = models.CharField(max_length=80)
    period = models.CharField(max_length=32)
    buyers = models.PositiveIntegerField(default=0)
    gmv = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("period", "cohort")


class AnomalyAlert(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    metric = models.ForeignKey(MetricDefinition, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=180)
    severity = models.CharField(max_length=16, default="medium")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    details = models.JSONField(default=dict, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class ExportSubscription(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="export_subscriptions")
    name = models.CharField(max_length=160)
    destination = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)


class ExecutiveScorecard(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    name = models.CharField(max_length=160)
    period = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    payload = models.JSONField(default=dict, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
