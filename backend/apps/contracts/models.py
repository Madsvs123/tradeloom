import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContractTemplate(TimeStampedModel):
    name = models.CharField(max_length=180)
    category = models.CharField(max_length=80, blank=True)
    body = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class LegalContract(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ACTIVE = "active", "Active"
        AMENDED = "amended", "Amended"
        RENEWED = "renewed", "Renewed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    template = models.ForeignKey(ContractTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name="agreements")
    number = models.CharField(max_length=40, unique=False, editable=False)
    title = models.CharField(max_length=180)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="buyer_contracts"
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplier_contracts"
    )
    currency = models.CharField(max_length=3, default="USD")
    total = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT, db_index=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    body = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number or self.title

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"CTR-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class ContractClause(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="clauses")
    heading = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=1)


class Amendment(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPLIED = "applied", "Applied"
        REJECTED = "rejected", "Rejected"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="amendments")
    summary = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    effective_on = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class Obligation(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="obligations")
    description = models.CharField(max_length=255)
    due_at = models.DateTimeField(null=True, blank=True)
    fulfilled = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class RenewalTerm(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="renewal_terms")
    notice_days = models.PositiveIntegerField(default=30)
    auto_renew = models.BooleanField(default=False)
    term_months = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class ContractType(TimeStampedModel):
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    default_notice_days = models.PositiveIntegerField(default=30)
    auto_renew_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ContractParty(TimeStampedModel):
    class PartyRole(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SUPPLIER = "supplier", "Supplier"
        AGENT = "agent", "Agent"
        OTHER = "other", "Other"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="parties")
    name = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=16, choices=PartyRole.choices, default=PartyRole.OTHER)
    is_primary = models.BooleanField(default=False)
    contact_details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("contract", "role", "name")

    def __str__(self):
        return f"{self.name} ({self.role}) on {self.contract.number}"


class ContractMilestone(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACHIEVED = "achieved", "Achieved"
        MISSED = "missed", "Missed"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    achieved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("contract", "due_at", "id")

    def __str__(self):
        return f"{self.contract.number}: {self.title}"

    def achieve(self):
        if self.status != self.Status.PENDING:
            raise ValidationError(f"Cannot achieve a milestone in status '{self.status}'.")
        self.status = self.Status.ACHIEVED
        self.achieved_at = timezone.now()
        self.save(update_fields=["status", "achieved_at", "updated_at"])
        return self

    def mark_missed(self):
        if self.status != self.Status.PENDING:
            raise ValidationError(f"Cannot mark a milestone in status '{self.status}' as missed.")
        self.status = self.Status.MISSED
        self.save(update_fields=["status", "updated_at"])
        return self


class ClauseLibrary(TimeStampedModel):
    name = models.CharField(max_length=180)
    category = models.CharField(max_length=80, blank=True)
    body = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="clause_library_entries"
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "clause library"

    def __str__(self):
        return self.name


class ExpiryAlert(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        TRIGGERED = "triggered", "Triggered"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="expiry_alerts")
    alert_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    triggered_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="acknowledged_expiry_alerts"
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-alert_at",)

    def __str__(self):
        return f"Expiry alert for {self.contract.number} at {self.alert_at}"

    def trigger(self):
        if self.status != self.Status.SCHEDULED:
            raise ValidationError("Only scheduled alerts can be triggered.")
        self.status = self.Status.TRIGGERED
        self.triggered_at = timezone.now()
        self.save(update_fields=["status", "triggered_at", "updated_at"])
        return self

    def acknowledge(self, user):
        if self.status != self.Status.TRIGGERED:
            raise ValidationError("Only triggered alerts can be acknowledged.")
        self.status = self.Status.ACKNOWLEDGED
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save(update_fields=["status", "acknowledged_by", "acknowledged_at", "updated_at"])
        return self


class ContractDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        EXECUTED = "executed", "Executed copy"
        DRAFT = "draft", "Draft"
        AMENDMENT = "amendment", "Amendment"
        SUPPORTING = "supporting", "Supporting"
        OTHER = "other", "Other"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=24, choices=DocumentType.choices, default=DocumentType.OTHER)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_contract_documents"
    )

    class Meta:
        ordering = ("contract", "version")

    def __str__(self):
        return self.title


class ContractApproval(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="contract_approvals")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    sequence = models.PositiveIntegerField(default=1)
    note = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("contract", "sequence")

    def __str__(self):
        return f"Approval {self.sequence} for {self.contract.number}"
