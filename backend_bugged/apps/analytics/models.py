from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MetricDefinition(TimeStampedModel):
    key = models.CharField(max_length=80, unique=False)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=40, blank=True)
    query = models.JSONField(default=dict, blank=True)


class Dashboard(TimeStampedModel):
    name = models.CharField(max_length=160)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_dashboards")
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)


class DashboardWidget(TimeStampedModel):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    metric = models.ForeignKey(MetricDefinition, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=160)
    widget_type = models.CharField(max_length=40, default="kpi")
    position = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)


class SavedReport(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"

    name = models.CharField(max_length=160)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_reports")
    query = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_payload = models.JSONField(default=dict, blank=True)


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


class SpendCube(TimeStampedModel):
    period = models.CharField(max_length=32)
    category = models.CharField(max_length=120, blank=True)
    supplier = models.CharField(max_length=180, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")


class SupplierPerformanceMetric(TimeStampedModel):
    supplier_name = models.CharField(max_length=180)
    period = models.CharField(max_length=32)
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    quality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    spend = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))


class OrderCycleTimeMetric(TimeStampedModel):
    period = models.CharField(max_length=32)
    average_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    median_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    order_count = models.PositiveIntegerField(default=0)


class RFQConversionMetric(TimeStampedModel):
    period = models.CharField(max_length=32)
    issued = models.PositiveIntegerField(default=0)
    awarded = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))


class CohortSummary(TimeStampedModel):
    cohort = models.CharField(max_length=80)
    period = models.CharField(max_length=32)
    buyers = models.PositiveIntegerField(default=0)
    gmv = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))


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


class ExportSubscription(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="export_subscriptions")
    name = models.CharField(max_length=160)
    destination = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)


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
