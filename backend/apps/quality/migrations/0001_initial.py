import decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InspectionPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(blank=True, max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("retired", "Retired"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inspection_plans_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inspection_plan_templates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Inspection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="scheduled",
                        max_length=16,
                    ),
                ),
                ("scheduled_at", models.DateTimeField()),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "overall_result",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pass", "Pass"),
                            ("conditional", "Conditional Pass"),
                            ("fail", "Fail"),
                        ],
                        max_length=16,
                        null=True,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "inspector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inspections_performed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inspections",
                        to="quality.inspectionplan",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inspections_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-scheduled_at",),
            },
        ),
        migrations.CreateModel(
            name="InspectionChecklist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("requirement", models.TextField(blank=True)),
                ("is_mandatory", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklists",
                        to="quality.inspectionplan",
                    ),
                ),
            ],
            options={
                "ordering": ("plan", "order", "id"),
            },
        ),
        migrations.CreateModel(
            name="InspectionItemResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("item_name", models.CharField(max_length=255)),
                (
                    "result",
                    models.CharField(
                        choices=[
                            ("pass", "Pass"),
                            ("fail", "Fail"),
                            ("na", "Not Applicable"),
                        ],
                        default="pass",
                        max_length=8,
                    ),
                ),
                ("actual_value", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("recorded_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "checklist",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="results",
                        to="quality.inspectionchecklist",
                    ),
                ),
                (
                    "inspection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="item_results",
                        to="quality.inspection",
                    ),
                ),
                (
                    "recorded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inspection_results_recorded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("inspection", "id"),
            },
        ),
        migrations.CreateModel(
            name="TestCertificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("certificate_number", models.CharField(blank=True, max_length=64)),
                ("product_description", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("revoked", "Revoked"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("valid_from", models.DateField(blank=True, null=True)),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("file_url", models.URLField(blank=True)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                (
                    "inspection",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="test_certificates",
                        to="quality.inspection",
                    ),
                ),
                (
                    "issued_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="test_certificates_issued",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="test_certificates_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="NonConformanceReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In Review"),
                            ("awaiting_action", "Awaiting Action"),
                            ("closed", "Closed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("minor", "Minor"),
                            ("major", "Major"),
                            ("critical", "Critical"),
                        ],
                        default="major",
                        max_length=12,
                    ),
                ),
                ("description", models.TextField()),
                ("root_cause", models.TextField(blank=True)),
                ("disposition", models.CharField(blank=True, max_length=24)),
                ("raised_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "inspection",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ncrs",
                        to="quality.inspection",
                    ),
                ),
                (
                    "raised_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ncrs_raised",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ncrs_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-raised_at",),
            },
        ),
        migrations.CreateModel(
            name="CorrectiveAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("corrective", "Corrective"),
                            ("preventive", "Preventive"),
                        ],
                        default="corrective",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In Progress"),
                            ("awaiting_verification", "Awaiting Verification"),
                            ("approved", "Approved"),
                            ("closed", "Closed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="open",
                        max_length=24,
                    ),
                ),
                ("description", models.TextField()),
                ("root_cause", models.TextField(blank=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("implementation_notes", models.TextField(blank=True)),
                ("verification_notes", models.TextField(blank=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="capa_approved",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "ncr",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="corrective_actions",
                        to="quality.nonconformancereport",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="capa_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="capa_verified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="QualityAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "audit_type",
                    models.CharField(
                        choices=[
                            ("internal", "Internal"),
                            ("supplier", "Supplier"),
                            ("process", "Process"),
                            ("system", "System"),
                        ],
                        default="supplier",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "Planned"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="planned",
                        max_length=16,
                    ),
                ),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                ("findings_summary", models.TextField(blank=True)),
                ("overall_result", models.CharField(blank=True, max_length=16)),
                (
                    "auditor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="quality_audits_performed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="quality_audits_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="SupplierQualityScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=7)),
                (
                    "score",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("100.00"),
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("inspection_count", models.PositiveIntegerField(default=0)),
                (
                    "inspection_pass_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("100.00"),
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("ncr_count", models.PositiveIntegerField(default=0)),
                ("capa_overdue_count", models.PositiveIntegerField(default=0)),
                ("computed_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "computed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quality_scores_computed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quality_scores",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-period",),
                "unique_together": {("supplier", "period")},
            },
        ),
        migrations.CreateModel(
            name="SamplingPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("product_description", models.CharField(blank=True, max_length=255)),
                ("standard", models.CharField(default="AQL ISO 2859-1", max_length=64)),
                ("inspection_level", models.CharField(default="II", max_length=8)),
                ("lot_size_min", models.PositiveIntegerField(default=0)),
                ("lot_size_max", models.PositiveIntegerField(default=0)),
                ("sample_size", models.PositiveIntegerField(default=0)),
                ("acceptance_number", models.PositiveIntegerField(default=0)),
                ("rejection_number", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("retired", "Retired"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sampling_plans_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sampling_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
