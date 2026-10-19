import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EsgProfile(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="esg_profiles")
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=64, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    reporting_period_start = models.DateField(null=True, blank=True)
    reporting_period_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    esg_rating = models.CharField(max_length=16, blank=True)
    summary = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.company_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ESG-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class CarbonFootprint(TimeStampedModel):
    class Scope(models.TextChoices):
        SCOPE_1 = "scope_1", "Scope 1 - Direct"
        SCOPE_2 = "scope_2", "Scope 2 - Indirect Energy"
        SCOPE_3 = "scope_3", "Scope 3 - Value Chain"
        TOTAL = "total", "Total"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        COMPUTED = "computed", "Computed"
        PUBLISHED = "published", "Published"

    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="carbon_footprints")
    scope = models.CharField(max_length=12, choices=Scope.choices, default=Scope.TOTAL)
    period = models.CharField(max_length=7)
    total_emissions_tco2e = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    baseline_emissions_tco2e = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    computed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("profile", "scope", "-period")
        unique_together = ("profile", "scope", "period")

    def __str__(self):
        return f"{self.profile.reference} - {self.scope} {self.period}: {self.total_emissions_tco2e}"


class EmissionRecord(TimeStampedModel):
    footprint = models.ForeignKey(CarbonFootprint, on_delete=models.CASCADE, related_name="emission_records")
    category = models.CharField(max_length=120)
    source = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=32, default="kWh")
    emission_factor = models.DecimalField(
        max_digits=12, decimal_places=4, default=Decimal("0.0000"), validators=[MinValueValidator(0)]
    )
    co2e = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("footprint", "id")

    def __str__(self):
        return f"{self.category} - {self.co2e} tCO2e"

    def save(self, *args, **kwargs):
        if self.quantity is not None and self.emission_factor is not None:
            self.co2e = (self.quantity * self.emission_factor).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)


class SustainabilityCertificate(TimeStampedModel):
    class CertificateType(models.TextChoices):
        ISO_14001 = "iso_14001", "ISO 14001"
        ISO_50001 = "iso_50001", "ISO 50001"
        B_CORP = "b_corp", "B Corp"
        LEED = "leed", "LEED"
        FSC = "fsc", "FSC"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="certificates")
    certificate_type = models.CharField(max_length=16, choices=CertificateType.choices, default=CertificateType.OTHER)
    certificate_number = models.CharField(max_length=64, blank=True)
    issuer = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    file_url = models.URLField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.certificate_type} - {self.certificate_number or self.profile.reference}"


class EsgTarget(TimeStampedModel):
    class Category(models.TextChoices):
        EMISSIONS = "emissions", "Emissions"
        ENERGY = "energy", "Energy"
        WATER = "water", "Water"
        WASTE = "waste", "Waste"
        SOCIAL = "social", "Social"
        GOVERNANCE = "governance", "Governance"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACHIEVED = "achieved", "Achieved"
        EXPIRED = "expired", "Expired"
        SUPERSEDED = "superseded", "Superseded"

    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="targets")
    category = models.CharField(max_length=16, choices=Category.choices, default=Category.EMISSIONS)
    metric = models.CharField(max_length=255)
    baseline_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    target_value = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    current_value = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=32, blank=True)
    target_date = models.DateField(null=True, blank=True)
    progress_percent = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ("profile", "category", "target_date")

    def __str__(self):
        return f"{self.metric} ({self.category})"


class GreenAttribute(TimeStampedModel):
    class AttributeType(models.TextChoices):
        RECYCLED_MATERIAL = "recycled_material", "Recycled Material"
        ECO_FRIENDLY = "eco_friendly", "Eco-Friendly"
        ENERGY_EFFICIENT = "energy_efficient", "Energy Efficient"
        WATER_SAVING = "water_saving", "Water Saving"
        BIODEGRADABLE = "biodegradable", "Biodegradable"
        CARBON_NEUTRAL = "carbon_neutral", "Carbon Neutral"
        OTHER = "other", "Other"

    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        SELF_DECLARED = "self_declared", "Self-Declared"
        THIRD_PARTY_VERIFIED = "third_party_verified", "Third-Party Verified"

    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="green_attributes")
    attribute_type = models.CharField(max_length=24, choices=AttributeType.choices, default=AttributeType.OTHER)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    verification_status = models.CharField(
        max_length=24, choices=VerificationStatus.choices, default=VerificationStatus.UNVERIFIED
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="green_attributes_verified",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("profile", "id")

    def __str__(self):
        return f"{self.name} ({self.attribute_type})"


class SustainabilityDeclaration(TimeStampedModel):
    class DeclarationType(models.TextChoices):
        SELF_DECLARATION = "self_declaration", "Self Declaration"
        ESG_REPORT = "esg_report", "ESG Report"
        CARBON_NEUTRALITY = "carbon_neutrality", "Carbon Neutrality"
        COMPLIANCE = "compliance", "Regulatory Compliance"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="declarations")
    declared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sustainability_declarations"
    )
    declaration_type = models.CharField(
        max_length=24, choices=DeclarationType.choices, default=DeclarationType.SELF_DECLARATION
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    statement = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sustainability_declarations_verified",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.declaration_type}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ESG-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class EsgReport(TimeStampedModel):
    class ReportType(models.TextChoices):
        ANNUAL = "annual", "Annual ESG Report"
        CARBON = "carbon", "Carbon Footprint Report"
        COMPLIANCE = "compliance", "Compliance Report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    profile = models.ForeignKey(EsgProfile, on_delete=models.CASCADE, related_name="esg_reports")
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=16, choices=ReportType.choices, default=ReportType.ANNUAL)
    period = models.CharField(max_length=7, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    summary = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="esg_reports_generated",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} ({self.period})"
