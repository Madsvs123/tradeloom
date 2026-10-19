import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TimeStampedModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MetricDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("key", models.CharField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("unit", models.CharField(blank=True, max_length=40)),
                ("query", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("key",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="KpiDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("key", models.CharField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("formula", models.CharField(blank=True, max_length=255)),
                ("unit", models.CharField(blank=True, max_length=40)),
                (
                    "direction",
                    models.CharField(
                        choices=[("up", "Higher is better"), ("down", "Lower is better")],
                        default="up",
                        max_length=16,
                    ),
                ),
                ("target_value", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("key",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Dashboard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_dashboards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="DashboardWidget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=160)),
                ("widget_type", models.CharField(default="kpi", max_length=40)),
                ("position", models.PositiveIntegerField(default=0)),
                ("config", models.JSONField(blank=True, default=dict)),
                (
                    "dashboard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="widgets",
                        to="analytics.dashboard",
                    ),
                ),
                (
                    "metric",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="analytics.metricdefinition",
                    ),
                ),
            ],
            options={
                "ordering": ("dashboard", "position"),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SavedReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("query", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("ready", "Ready")], default="draft", max_length=16
                    ),
                ),
                ("last_run_at", models.DateTimeField(blank=True, null=True)),
                ("last_payload", models.JSONField(blank=True, default=dict)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReportBuilderDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("source", models.CharField(default="spend_cube", max_length=80)),
                ("dimensions", models.JSONField(blank=True, default=list)),
                ("measures", models.JSONField(blank=True, default=list)),
                ("filters", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")], default="draft", max_length=16
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="report_builder_definitions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ExportJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "export_format",
                    models.CharField(
                        choices=[("csv", "CSV"), ("xlsx", "XLSX"), ("pdf", "PDF")], default="csv", max_length=16
                    ),
                ),
                ("filters", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=16,
                    ),
                ),
                ("file_url", models.URLField(blank=True)),
                ("row_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_export_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="export_jobs",
                        to="analytics.savedreport",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReportSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cron", models.CharField(default="0 8 * * 1", max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                ("recipients", models.JSONField(blank=True, default=list)),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="analytics.savedreport",
                    ),
                ),
            ],
            options={},
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="AnalyticsSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("captured_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("value", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("dimensions", models.JSONField(blank=True, default=dict)),
                (
                    "metric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snapshots",
                        to="analytics.metricdefinition",
                    ),
                ),
            ],
            options={
                "ordering": ("-captured_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ComparisonPeriod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("base_period", models.CharField(max_length=32)),
                ("comparison_period", models.CharField(max_length=32)),
                ("metric_keys", models.JSONField(blank=True, default=list)),
                ("variance", models.JSONField(blank=True, default=dict)),
                ("computed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="comparison_periods",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("base_period", "comparison_period")},
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ForecastModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("horizon_days", models.PositiveIntegerField(default=30)),
                ("algorithm", models.CharField(default="linear", max_length=80)),
                ("params", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("trained", "Trained"),
                            ("active", "Active"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("last_forecast_at", models.DateTimeField(blank=True, null=True)),
                (
                    "metric",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="forecast_models",
                        to="analytics.metricdefinition",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="forecast_models",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ForecastProjection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("predicted_value", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("confidence_low", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("confidence_high", models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ("actual_value", models.DecimalField(blank=True, decimal_places=4, max_digits=16, null=True)),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projections",
                        to="analytics.forecastmodel",
                    ),
                ),
            ],
            options={
                "ordering": ("period",),
                "unique_together": {("model", "period")},
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SpendCube",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("category", models.CharField(blank=True, max_length=120)),
                ("supplier", models.CharField(blank=True, max_length=180)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
            ],
            options={
                "ordering": ("period", "category"),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SupplierPerformanceMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("supplier_name", models.CharField(max_length=180)),
                ("period", models.CharField(max_length=32)),
                ("on_time_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("quality_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("spend", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
            ],
            options={
                "ordering": ("period", "supplier_name"),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="OrderCycleTimeMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("average_hours", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("median_hours", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("order_count", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ("period",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RFQConversionMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("issued", models.PositiveIntegerField(default=0)),
                ("awarded", models.PositiveIntegerField(default=0)),
                ("conversion_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
            ],
            options={
                "ordering": ("period",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CohortSummary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cohort", models.CharField(max_length=80)),
                ("period", models.CharField(max_length=32)),
                ("buyers", models.PositiveIntegerField(default=0)),
                ("gmv", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
            ],
            options={
                "ordering": ("period", "cohort"),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="AnomalyAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("severity", models.CharField(default="medium", max_length=16)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("acknowledged", "Acknowledged"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("details", models.JSONField(blank=True, default=dict)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "metric",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="analytics.metricdefinition",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ExportSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("destination", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("analytics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ExecutiveScorecard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("period", models.CharField(max_length=32)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")], default="draft", max_length=16
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("analytics", "TimeStampedModel"),
        ),
    ]
