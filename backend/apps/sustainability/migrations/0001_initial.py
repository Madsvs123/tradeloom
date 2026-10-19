import decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EsgProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("company_name", models.CharField(max_length=255)),
                ("industry", models.CharField(blank=True, max_length=120)),
                ("country", models.CharField(blank=True, max_length=64)),
                ("employee_count", models.PositiveIntegerField(blank=True, null=True)),
                ("reporting_period_start", models.DateField(blank=True, null=True)),
                ("reporting_period_end", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("esg_rating", models.CharField(blank=True, max_length=16)),
                ("summary", models.TextField(blank=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="esg_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CarbonFootprint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "scope",
                    models.CharField(
                        choices=[
                            ("scope_1", "Scope 1 - Direct"),
                            ("scope_2", "Scope 2 - Indirect Energy"),
                            ("scope_3", "Scope 3 - Value Chain"),
                            ("total", "Total"),
                        ],
                        default="total",
                        max_length=12,
                    ),
                ),
                ("period", models.CharField(max_length=7)),
                (
                    "total_emissions_tco2e",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "baseline_emissions_tco2e",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=14,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("computed", "Computed"),
                            ("published", "Published"),
                        ],
                        default="draft",
                        max_length=12,
                    ),
                ),
                ("computed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="carbon_footprints",
                        to="sustainability.esgprofile",
                    ),
                ),
            ],
            options={
                "ordering": ("profile", "scope", "-period"),
                "unique_together": {("profile", "scope", "period")},
            },
        ),
        migrations.CreateModel(
            name="EmissionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.CharField(max_length=120)),
                ("source", models.CharField(blank=True, max_length=255)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("unit", models.CharField(default="kWh", max_length=32)),
                (
                    "emission_factor",
                    models.DecimalField(
                        decimal_places=4,
                        default=decimal.Decimal("1.0000"),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "co2e",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "footprint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emission_records",
                        to="sustainability.carbonfootprint",
                    ),
                ),
            ],
            options={
                "ordering": ("footprint", "id"),
            },
        ),
        migrations.CreateModel(
            name="SustainabilityCertificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "certificate_type",
                    models.CharField(
                        choices=[
                            ("iso_14001", "ISO 14001"),
                            ("iso_50001", "ISO 50001"),
                            ("b_corp", "B Corp"),
                            ("leed", "LEED"),
                            ("fsc", "FSC"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=16,
                    ),
                ),
                ("certificate_number", models.CharField(blank=True, max_length=64)),
                ("issuer", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("expired", "Expired"),
                            ("revoked", "Revoked"),
                        ],
                        default="draft",
                        max_length=12,
                    ),
                ),
                ("issued_at", models.DateField(blank=True, null=True)),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("file_url", models.URLField(blank=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificates",
                        to="sustainability.esgprofile",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="EsgTarget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("emissions", "Emissions"),
                            ("energy", "Energy"),
                            ("water", "Water"),
                            ("waste", "Waste"),
                            ("social", "Social"),
                            ("governance", "Governance"),
                        ],
                        default="emissions",
                        max_length=16,
                    ),
                ),
                ("metric", models.CharField(max_length=255)),
                ("baseline_value", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "target_value",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "current_value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("unit", models.CharField(blank=True, max_length=32)),
                ("target_date", models.DateField(blank=True, null=True)),
                (
                    "progress_percent",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("achieved", "Achieved"),
                            ("expired", "Expired"),
                            ("superseded", "Superseded"),
                        ],
                        default="active",
                        max_length=12,
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="targets",
                        to="sustainability.esgprofile",
                    ),
                ),
            ],
            options={
                "ordering": ("profile", "category", "target_date"),
            },
        ),
        migrations.CreateModel(
            name="GreenAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "attribute_type",
                    models.CharField(
                        choices=[
                            ("recycled_material", "Recycled Material"),
                            ("eco_friendly", "Eco-Friendly"),
                            ("energy_efficient", "Energy Efficient"),
                            ("water_saving", "Water Saving"),
                            ("biodegradable", "Biodegradable"),
                            ("carbon_neutral", "Carbon Neutral"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=24,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "verification_status",
                    models.CharField(
                        choices=[
                            ("unverified", "Unverified"),
                            ("self_declared", "Self-Declared"),
                            ("third_party_verified", "Third-Party Verified"),
                        ],
                        default="unverified",
                        max_length=24,
                    ),
                ),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="green_attributes",
                        to="sustainability.esgprofile",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="green_attributes_verified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("profile", "id"),
            },
        ),
        migrations.CreateModel(
            name="SustainabilityDeclaration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "declaration_type",
                    models.CharField(
                        choices=[
                            ("self_declaration", "Self Declaration"),
                            ("esg_report", "ESG Report"),
                            ("carbon_neutrality", "Carbon Neutrality"),
                            ("compliance", "Regulatory Compliance"),
                        ],
                        default="self_declaration",
                        max_length=24,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                            ("withdrawn", "Withdrawn"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("statement", models.TextField(blank=True)),
                ("verification_notes", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "declared_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sustainability_declarations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="declarations",
                        to="sustainability.esgprofile",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sustainability_declarations_verified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="EsgReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("annual", "Annual ESG Report"),
                            ("carbon", "Carbon Footprint Report"),
                            ("compliance", "Compliance Report"),
                            ("other", "Other"),
                        ],
                        default="annual",
                        max_length=16,
                    ),
                ),
                ("period", models.CharField(blank=True, max_length=7)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=12,
                    ),
                ),
                ("summary", models.TextField(blank=True)),
                ("file_url", models.URLField(blank=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "generated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="esg_reports_generated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="esg_reports",
                        to="sustainability.esgprofile",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
