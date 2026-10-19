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
            name="ComplianceParty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                (
                    "kind",
                    models.CharField(
                        choices=[("company", "Company"), ("person", "Person")], default="company", max_length=16
                    ),
                ),
                ("country", models.CharField(blank=True, max_length=2)),
                ("registration_number", models.CharField(blank=True, max_length=80)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="compliance_parties",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ScreeningCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("list_name", models.CharField(max_length=120)),
                ("reason", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In review"),
                            ("cleared", "Cleared"),
                            ("hit", "Hit"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("matched_records", models.JSONField(blank=True, default=list)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decided_screening_cases",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="screening_cases",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ComplianceTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
                        default="normal",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In progress"),
                            ("complete", "Complete"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("related_type", models.CharField(blank=True, max_length=80)),
                ("related_id", models.CharField(blank=True, max_length=64)),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="compliance_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="compliance_tasks",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RiskAssessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("methodology", models.CharField(default="standard", max_length=120)),
                ("overall_score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("band", models.CharField(default="low", max_length=16)),
                ("findings", models.JSONField(blank=True, default=list)),
                ("recommendations", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assessor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="risk_assessments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decided_risk_assessments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="risk_assessments",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SanctionsList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("authority", models.CharField(blank=True, max_length=160)),
                ("country", models.CharField(blank=True, max_length=2)),
                (
                    "list_type",
                    models.CharField(
                        choices=[
                            ("sanctions", "Sanctions"),
                            ("pep", "PEP"),
                            ("adverse_media", "Adverse media"),
                        ],
                        default="sanctions",
                        max_length=16,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SanctionsEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=180)),
                ("aliases", models.JSONField(blank=True, default=list)),
                ("id_number", models.CharField(blank=True, max_length=80)),
                ("country", models.CharField(blank=True, max_length=2)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("matched", "Matched"), ("cleared", "Cleared")],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "matched_case",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="matched_entries",
                        to="compliance.screeningcase",
                    ),
                ),
                (
                    "sanctions_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="compliance.sanctionslist",
                    ),
                ),
            ],
            options={
                "ordering": ("full_name",),
                "unique_together": {("sanctions_list", "full_name")},
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="EvidenceFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("case_type", models.CharField(max_length=80)),
                ("case_id", models.CharField(blank=True, max_length=64)),
                ("title", models.CharField(max_length=180)),
                ("file_url", models.URLField()),
                ("description", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evidence_files",
                        to="compliance.complianceparty",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_evidence_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RiskScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("band", models.CharField(default="low", max_length=16)),
                ("rationale", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="risk_scores",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="KYBCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In review"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="kyb_cases", to="compliance.complianceparty"
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="KYCCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In review"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="kyc_cases", to="compliance.complianceparty"
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="BeneficialOwner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=180)),
                ("ownership_percent", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("nationality", models.CharField(blank=True, max_length=2)),
                ("is_controlling", models.BooleanField(default=False)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="beneficial_owners",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-ownership_percent",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SupplierDueDiligence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("complete", "Complete")], default="open", max_length=16
                    ),
                ),
                ("questionnaire", models.JSONField(blank=True, default=dict)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="due_diligence",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ComplianceDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("document_type", models.CharField(max_length=80)),
                ("file_url", models.URLField()),
                (
                    "status",
                    models.CharField(
                        choices=[("uploaded", "Uploaded"), ("verified", "Verified"), ("rejected", "Rejected")],
                        default="uploaded",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="compliance.complianceparty",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WatchlistScreening",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("list_name", models.CharField(max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[("clear", "Clear"), ("hit", "Hit"), ("review", "Review")],
                        default="clear",
                        max_length=16,
                    ),
                ),
                ("matches", models.JSONField(blank=True, default=list)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="screenings",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CompliancePolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("body", models.TextField(blank=True)),
                ("version", models.CharField(default="1.0", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="TaxForm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("form_type", models.CharField(max_length=40)),
                ("year", models.PositiveIntegerField()),
                ("file_url", models.URLField(blank=True)),
                ("is_certified", models.BooleanField(default=False)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="tax_forms", to="compliance.complianceparty"
                    ),
                ),
            ],
            options={
                "unique_together": {("party", "form_type", "year")},
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InsuranceCertificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("insurer", models.CharField(max_length=160)),
                ("policy_number", models.CharField(max_length=80)),
                ("coverage_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("expires_at", models.DateField(blank=True, null=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="insurance_certificates",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="QualityAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=160)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In progress"),
                            ("passed", "Passed"),
                            ("failed", "Failed"),
                        ],
                        default="scheduled",
                        max_length=16,
                    ),
                ),
                ("score", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audits",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CorrectiveAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("in_progress", "In progress"), ("closed", "Closed")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "audit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="corrective_actions",
                        to="compliance.qualityaudit",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="IncidentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                (
                    "severity",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
                        default="medium",
                        max_length=16,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("occurred_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("resolved", models.BooleanField(default=False)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incidents",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={
                "ordering": ("-occurred_at",),
            },
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="DataRetentionRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("request_type", models.CharField(default="delete", max_length=40)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("completed", "Completed"), ("denied", "Denied")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="retention_requests",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ExportComplianceCheck",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("destination_country", models.CharField(max_length=2)),
                ("product_code", models.CharField(blank=True, max_length=40)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("cleared", "Cleared"), ("blocked", "Blocked")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="export_checks",
                        to="compliance.complianceparty",
                    ),
                ),
            ],
            options={},
            bases=("compliance", "TimeStampedModel"),
        ),
    ]
