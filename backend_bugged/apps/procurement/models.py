from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DepartmentBudget(TimeStampedModel):
    department = models.CharField(max_length=120)
    fiscal_year = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="USD")
    allocated = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    spent = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class PurchasingPolicy(TimeStampedModel):
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    max_unapproved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    requires_committee = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


class ApprovalRule(TimeStampedModel):
    policy = models.ForeignKey(PurchasingPolicy, on_delete=models.PROTECT, related_name="rules")
    min_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    approver_role = models.CharField(max_length=80)
    sequence = models.PositiveIntegerField(default=1)


class PreferredSupplierProgram(TimeStampedModel):
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


class Supplier(TimeStampedModel):
    class Status(models.TextChoices):
        PROSPECT = "prospect", "Prospect"
        ONBOARDING = "onboarding", "Onboarding"
        APPROVED = "approved", "Approved"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=180)
    legal_name = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PROSPECT)
    country = models.CharField(max_length=2, blank=True)
    preferred_program = models.ForeignKey(
        PreferredSupplierProgram, null=True, blank=True, on_delete=models.SET_NULL, related_name="suppliers"
    )
    contact_email = models.EmailField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class SupplierOnboardingChecklist(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETE = "complete", "Complete"

    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name="onboarding")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    kyb_complete = models.BooleanField(default=False)
    insurance_complete = models.BooleanField(default=False)
    tax_complete = models.BooleanField(default=False)
    capabilities_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)


class SupplierScorecard(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="scorecards")
    period = models.CharField(max_length=32)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    delivery_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    cost_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)


class BuyingCommittee(TimeStampedModel):
    name = models.CharField(max_length=160)
    department = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)


class BuyingCommitteeMember(TimeStampedModel):
    committee = models.ForeignKey(BuyingCommittee, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=80, default="member")
    can_decide = models.BooleanField(default=True)


class PurchaseRequisition(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CONVERTED = "converted", "Converted"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=32, unique=True, editable=False)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requisitions")
    department = models.CharField(max_length=120, blank=True)
    budget = models.ForeignKey(DepartmentBudget, null=True, blank=True, on_delete=models.SET_NULL)
    policy = models.ForeignKey(PurchasingPolicy, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    justification = models.TextField(blank=True)
    needed_by = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number


class PurchaseRequisitionLine(TimeStampedModel):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="lines")
    sku = models.CharField(max_length=80, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("1.000"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")


class ApprovalWorkflow(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="workflows")
    rule = models.ForeignKey(ApprovalRule, null=True, blank=True, on_delete=models.SET_NULL)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    decision_note = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)


class RequisitionToRFQConversion(TimeStampedModel):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="rfq_conversions")
    rfq_id = models.PositiveIntegerField(null=True, blank=True)
    converted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)


class ProcurementEvent(TimeStampedModel):
    requisition = models.ForeignKey(
        PurchaseRequisition, null=True, blank=True, on_delete=models.CASCADE, related_name="events"
    )
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default={}, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class SpendControl(TimeStampedModel):
    department = models.CharField(max_length=120)
    category = models.CharField(max_length=120, blank=True)
    max_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
