from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ComplianceParty(TimeStampedModel):
    class Kind(models.TextChoices):
        COMPANY = "company", "Company"
        PERSON = "person", "Person"

    name = models.CharField(max_length=180)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.COMPANY)
    country = models.CharField(max_length=2, blank=True)
    registration_number = models.CharField(max_length=80, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class RiskScore(TimeStampedModel):
    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="risk_scores")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    band = models.CharField(max_length=16, default="low")
    rationale = models.TextField(blank=True)


class KYBCase(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="kyb_cases")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)


class KYCCase(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="kyc_cases")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)


class BeneficialOwner(TimeStampedModel):
    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="beneficial_owners")
    full_name = models.CharField(max_length=180)
    ownership_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    nationality = models.CharField(max_length=2, blank=True)
    is_controlling = models.BooleanField(default=False)


class SupplierDueDiligence(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETE = "complete", "Complete"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="due_diligence")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    questionnaire = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class ComplianceDocument(TimeStampedModel):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=80)
    file_url = models.URLField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UPLOADED)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    rejection_reason = models.TextField(blank=True)


class WatchlistScreening(TimeStampedModel):
    class Status(models.TextChoices):
        CLEAR = "clear", "Clear"
        HIT = "hit", "Hit"
        REVIEW = "review", "Review"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="screenings")
    list_name = models.CharField(max_length=120)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CLEAR)
    matches = models.JSONField(default=list, blank=True)


class CompliancePolicy(TimeStampedModel):
    name = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)


class TaxForm(TimeStampedModel):
    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="tax_forms")
    form_type = models.CharField(max_length=40)
    year = models.PositiveIntegerField()
    file_url = models.URLField(blank=True)
    is_certified = models.BooleanField(default=False)


class InsuranceCertificate(TimeStampedModel):
    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="insurance_certificates")
    insurer = models.CharField(max_length=160)
    policy_number = models.CharField(max_length=80)
    coverage_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    expires_at = models.DateField(null=True, blank=True)


class QualityAudit(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In progress"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="audits")
    title = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)


class CorrectiveAction(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        CLOSED = "closed", "Closed"

    audit = models.ForeignKey(QualityAudit, on_delete=models.CASCADE, related_name="corrective_actions")
    description = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    due_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)


class IncidentRecord(TimeStampedModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="incidents")
    title = models.CharField(max_length=180)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)


class DataRetentionRequest(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"
        DENIED = "denied", "Denied"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="retention_requests")
    request_type = models.CharField(max_length=40, default="delete")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    notes = models.TextField(blank=True)


class ExportComplianceCheck(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CLEARED = "cleared", "Cleared"
        BLOCKED = "blocked", "Blocked"

    party = models.ForeignKey(ComplianceParty, on_delete=models.CASCADE, related_name="export_checks")
    destination_country = models.CharField(max_length=2)
    product_code = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
