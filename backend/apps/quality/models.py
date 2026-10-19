import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InspectionPlan(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        RETIRED = "retired", "Retired"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspection_plans_created"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspection_plan_templates",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class Inspection(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        CONDITIONAL = "conditional", "Conditional Pass"
        FAIL = "fail", "Fail"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    plan = models.ForeignKey(
        InspectionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="inspections"
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspections_received"
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspections_performed"
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    overall_result = models.CharField(
        max_length=16, choices=Result.choices, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-scheduled_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class InspectionChecklist(TimeStampedModel):
    plan = models.ForeignKey(
        InspectionPlan, on_delete=models.CASCADE, related_name="checklists", null=True, blank=True
    )
    title = models.CharField(max_length=255)
    requirement = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("plan", "order", "id")

    def __str__(self):
        return self.title


class InspectionItemResult(TimeStampedModel):
    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        NA = "na", "Not Applicable"

    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="item_results")
    checklist = models.ForeignKey(
        InspectionChecklist, on_delete=models.SET_NULL, null=True, blank=True, related_name="results"
    )
    item_name = models.CharField(max_length=255)
    result = models.CharField(max_length=8, choices=Result.choices, default=Result.FAIL)
    actual_value = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspection_results_recorded"
    )
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("inspection", "id")

    def __str__(self):
        return f"{self.inspection.reference} - {self.item_name}: {self.result}"


class TestCertificate(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        REVOKED = "revoked", "Revoked"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    inspection = models.ForeignKey(
        Inspection, on_delete=models.SET_NULL, null=True, blank=True, related_name="test_certificates"
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="test_certificates_received"
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="test_certificates_issued"
    )
    certificate_number = models.CharField(max_length=64, blank=True)
    product_description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    file_url = models.URLField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.product_description or self.supplier}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class NonConformanceReport(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In Review"
        AWAITING_ACTION = "awaiting_action", "Awaiting Action"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    class Severity(models.TextChoices):
        MINOR = "minor", "Minor"
        MAJOR = "major", "Major"
        CRITICAL = "critical", "Critical"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    inspection = models.ForeignKey(
        Inspection, on_delete=models.SET_NULL, null=True, blank=True, related_name="ncrs"
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ncrs_received"
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ncrs_raised"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    severity = models.CharField(max_length=12, choices=Severity.choices, default=Severity.MAJOR)
    description = models.TextField()
    root_cause = models.TextField(blank=True)
    disposition = models.CharField(max_length=24, blank=True)
    raised_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-raised_at",)

    def __str__(self):
        return f"{self.reference} - {self.severity}: {self.description[:60]}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class CorrectiveAction(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        AWAITING_VERIFICATION = "awaiting_verification", "Awaiting Verification"
        APPROVED = "approved", "Approved"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    class ActionType(models.TextChoices):
        CORRECTIVE = "corrective", "Corrective"
        PREVENTIVE = "preventive", "Preventive"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    ncr = models.ForeignKey(
        NonConformanceReport,
        on_delete=models.CASCADE,
        related_name="corrective_actions",
        null=True,
        blank=True,
    )
    action_type = models.CharField(max_length=16, choices=ActionType.choices, default=ActionType.CORRECTIVE)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    description = models.TextField()
    root_cause = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="capa_owned")
    due_date = models.DateField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="capa_approved"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="capa_verified"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.description[:60]}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class QualityAudit(TimeStampedModel):
    class AuditType(models.TextChoices):
        INTERNAL = "internal", "Internal"
        SUPPLIER = "supplier", "Supplier"
        PROCESS = "process", "Process"
        SYSTEM = "system", "System"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="quality_audits_received"
    )
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="quality_audits_performed"
    )
    audit_type = models.CharField(max_length=16, choices=AuditType.choices, default=AuditType.SUPPLIER)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PLANNED)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    findings_summary = models.TextField(blank=True)
    overall_result = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.audit_type}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class SupplierQualityScore(TimeStampedModel):
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quality_scores"
    )
    period = models.CharField(max_length=7)
    score = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("100.00"), validators=[MinValueValidator(0)]
    )
    inspection_count = models.PositiveIntegerField(default=0)
    inspection_pass_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("100.00"), validators=[MinValueValidator(0)]
    )
    ncr_count = models.PositiveIntegerField(default=0)
    capa_overdue_count = models.PositiveIntegerField(default=0)
    computed_at = models.DateTimeField(default=timezone.now)
    computed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quality_scores_computed",
    )

    class Meta:
        ordering = ("-period",)
        unique_together = ("supplier", "period")

    def __str__(self):
        return f"{self.supplier} - {self.period}: {self.score}"


class SamplingPlan(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        RETIRED = "retired", "Retired"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sampling_plans"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sampling_plans_created"
    )
    product_description = models.CharField(max_length=255, blank=True)
    standard = models.CharField(max_length=64, default="AQL ISO 2859-1")
    inspection_level = models.CharField(max_length=8, default="II")
    lot_size_min = models.PositiveIntegerField(default=0)
    lot_size_max = models.PositiveIntegerField(default=0)
    sample_size = models.PositiveIntegerField(default=0)
    acceptance_number = models.PositiveIntegerField(default=0)
    rejection_number = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.product_description or self.standard}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"QLT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
