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


class LetterOfCredit(TimeStampedModel):
    class LcType(models.TextChoices):
        SIGHT = "sight", "Sight"
        USANCE = "usance", "Usance"
        STANDBY = "standby", "Standby"
        REVOLVING = "revolving", "Revolving"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        AMENDED = "amended", "Amended"
        CONFIRMED = "confirmed", "Confirmed"
        NEGOTIATED = "negotiated", "Negotiated"
        MATURED = "matured", "Matured"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lcs_applicant"
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lcs_beneficiary"
    )
    lc_type = models.CharField(max_length=16, choices=LcType.choices, default=LcType.SIGHT)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    issuing_bank = models.CharField(max_length=255, blank=True)
    advising_bank = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    expiry_date = models.DateField()
    latest_shipment_date = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True)
    document_requirements = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class LcAmendment(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        APPLIED = "applied", "Applied"

    lc = models.ForeignKey(LetterOfCredit, on_delete=models.CASCADE, related_name="amendments")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    amendment_type = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    new_amount = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    new_expiry_date = models.DateField(null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lc_amendments_requested"
    )
    requested_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lc_amendments_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-requested_at",)

    def __str__(self):
        return f"{self.lc.reference} - {self.amendment_type}"


class BankGuarantee(TimeStampedModel):
    class GuaranteeType(models.TextChoices):
        BID = "bid", "Bid Bond"
        PERFORMANCE = "performance", "Performance"
        ADVANCE_PAYMENT = "advance_payment", "Advance Payment"
        WARRANTY = "warranty", "Warranty"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        CLAIMED = "claimed", "Claimed"
        RELEASED = "released", "Released"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="guarantees_applicant"
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="guarantees_beneficiary"
    )
    guarantee_type = models.CharField(max_length=20, choices=GuaranteeType.choices, default=GuaranteeType.PERFORMANCE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    bank = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    claim_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.guarantee_type}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class InvoiceFinancingRequest(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        OFFERED = "offered", "Offered"
        ACCEPTED = "accepted", "Accepted"
        FUNDED = "funded", "Funded"
        REPAID = "repaid", "Repaid"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="financing_requests"
    )
    invoice_reference = models.CharField(max_length=64)
    invoice_amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    requested_amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    requested_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("5.00"), validators=[MinValueValidator(0)]
    )
    tenor_days = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    funded_at = models.DateTimeField(null=True, blank=True)
    repaid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.invoice_reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class FinancingOffer(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    request = models.ForeignKey(InvoiceFinancingRequest, on_delete=models.CASCADE, related_name="offers")
    offered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="financing_offers"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    rate = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    tenor_days = models.PositiveIntegerField(default=30)
    fees = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    valid_until = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Offer {self.pk} on {self.request.reference}"


class FactoringAgreement(TimeStampedModel):
    class AgreementType(models.TextChoices):
        RECOURSE = "recourse", "Recourse"
        NON_RECOURSE = "non_recourse", "Non-Recourse"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        TERMINATED = "terminated", "Terminated"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="factoring_agreements"
    )
    factor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="factoring_factor_for"
    )
    agreement_type = models.CharField(max_length=16, choices=AgreementType.choices, default=AgreementType.RECOURSE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    credit_limit = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    advance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("50.00"), validators=[MinValueValidator(0)]
    )
    discount_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("3.00"), validators=[MinValueValidator(0)]
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.supplier}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class CreditInsurancePolicy(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    insured = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="credit_insurance_policies"
    )
    insurer = models.CharField(max_length=255, blank=True)
    policy_number = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    coverage_limit = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    premium = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.insurer or 'Unassigned'}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class FinanceDisbursement(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        DISBURSED = "disbursed", "Disbursed"
        FAILED = "failed", "Failed"

    class Method(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        WIRE = "wire", "Wire"
        CHECK = "check", "Check"
        OTHER = "other", "Other"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    request = models.ForeignKey(
        InvoiceFinancingRequest,
        on_delete=models.CASCADE,
        related_name="disbursements",
        null=True,
        blank=True,
    )
    agreement = models.ForeignKey(
        FactoringAgreement, on_delete=models.CASCADE, related_name="disbursements", null=True, blank=True
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="finance_disbursements"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    method = models.CharField(max_length=16, choices=Method.choices, default=Method.BANK_TRANSFER)
    amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    disbursed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class RepaymentSchedule(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        DUE = "due", "Due"
        PAID = "paid", "Paid"
        LATE = "late", "Late"
        DEFAULTED = "defaulted", "Defaulted"

    request = models.ForeignKey(
        InvoiceFinancingRequest, on_delete=models.CASCADE, related_name="repayment_schedules"
    )
    due_date = models.DateField()
    principal = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    interest = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_due = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    paid_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repayments_recorded",
    )

    class Meta:
        ordering = ("due_date", "id")

    def __str__(self):
        return f"{self.request.reference} - {self.due_date}: {self.total_due}"
