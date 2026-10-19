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
        ordering = ("created_at",)

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


class SourcingRequest(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        IN_PROGRESS = "in_progress", "In progress"
        CONVERTED = "converted", "Converted"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sourcing_requests")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    category = models.ForeignKey("SpendCategory", null=True, blank=True, on_delete=models.SET_NULL, related_name="sourcing_requests")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    required_by = models.DateField(null=True, blank=True)
    conversion_target = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SR{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def submit(self):
        if self.status != self.Status.DRAFT:
            raise ValidationError(f"Cannot submit a sourcing request in status '{self.status}'.")
        if self.estimated_value <= 0:
            raise ValidationError("Estimated value must be positive before submission.")
        self.status = self.Status.SUBMITTED
        self.save(update_fields=["status", "updated_at"])
        return self

    def cancel(self):
        if self.status in (self.Status.CONVERTED, self.Status.CANCELLED):
            raise ValidationError("This sourcing request can no longer be cancelled.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
        return self

    def mark_in_progress(self):
        if self.status != self.Status.SUBMITTED:
            raise ValidationError("Only submitted sourcing requests can be moved to in progress.")
        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=["status", "updated_at"])
        return self

    def convert(self):
        if self.status not in (self.Status.SUBMITTED, self.Status.IN_PROGRESS):
            raise ValidationError("Only submitted or in-progress sourcing requests can be converted.")
        self.status = self.Status.CONVERTED
        self.save(update_fields=["status", "updated_at"])
        return self


class BudgetLine(TimeStampedModel):
    budget = models.ForeignKey(DepartmentBudget, on_delete=models.CASCADE, related_name="lines")
    name = models.CharField(max_length=160)
    category = models.ForeignKey("SpendCategory", null=True, blank=True, on_delete=models.SET_NULL, related_name="budget_lines")
    allocated = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    committed = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    spent = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("budget", "name")

    def __str__(self):
        return f"{self.budget.department} / {self.name}"

    @property
    def remaining(self):
        return self.allocated - self.committed - self.spent

    def commit(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Commitment amount must be positive.")
        if amount >= self.remaining:
            raise ValidationError("Budget line would be exceeded by this commitment.")
        self.committed += amount
        self.save(update_fields=["committed", "updated_at"])
        return self

    def release(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0 or amount > self.committed:
            raise ValidationError("Release amount must be positive and no more than the committed amount.")
        self.committed -= amount
        self.save(update_fields=["committed", "updated_at"])
        return self

    def record_spend(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValidationError("Spend amount must be positive.")
        if amount > self.committed:
            raise ValidationError("Spend exceeds the committed amount on this budget line.")
        self.spent += amount
        self.committed -= amount
        self.save(update_fields=["spent", "committed", "updated_at"])
        return self


class PolicyRule(TimeStampedModel):
    class RuleType(models.TextChoices):
        APPROVAL = "approval", "Approval threshold"
        COMMITTEE = "committee", "Committee review"
        RESTRICTION = "restriction", "Category restriction"
        QUOTE = "quote", "Minimum quotes"

    policy = models.ForeignKey(PurchasingPolicy, on_delete=models.CASCADE, related_name="policy_rules")
    rule_type = models.CharField(max_length=24, choices=RuleType.choices)
    threshold_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    min_quotes = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey("SpendCategory", null=True, blank=True, on_delete=models.SET_NULL, related_name="policy_rules")
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("policy", "id")

    def __str__(self):
        return f"{self.policy.name}: {self.rule_type}"


class ContractCoverageCheck(TimeStampedModel):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="coverage_checks")
    contract_id = models.PositiveIntegerField(null=True, blank=True)
    contract_number = models.CharField(max_length=64, blank=True)
    is_covered = models.BooleanField(default=False)
    coverage_type = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Coverage for {self.requisition.number}: {self.is_covered}"


class SpendCategory(TimeStampedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "spend categories"
        constraints = (
            models.UniqueConstraint(fields=("name",), name="procurement_unique_spend_category_name"),
        )

    def __str__(self):
        return self.name


class SavingsTracking(TimeStampedModel):
    class SavingsType(models.TextChoices):
        NEGOTIATED = "negotiated", "Negotiated"
        PRICE_DROP = "price_drop", "Price drop"
        VOLUME = "volume", "Volume consolidation"
        PROCESS = "process", "Process efficiency"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ESTIMATED = "estimated", "Estimated"
        REALIZED = "realized", "Realized"
        VOID = "void", "Void"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    title = models.CharField(max_length=180)
    savings_type = models.CharField(max_length=24, choices=SavingsType.choices, default=SavingsType.OTHER)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ESTIMATED)
    currency = models.CharField(max_length=3, default="USD")
    estimated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    realized_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    category = models.ForeignKey(SpendCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="savings")
    requisition = models.ForeignKey(PurchaseRequisition, null=True, blank=True, on_delete=models.SET_NULL, related_name="savings")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="savings_tracked")
    realized_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SV-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def realize(self):
        if self.status != self.Status.ESTIMATED:
            raise ValidationError(f"Cannot realize savings in status '{self.status}'.")
        if self.realized_amount <= 0:
            raise ValidationError("Realized amount must be positive.")
        self.status = self.Status.REALIZED
        self.realized_at = timezone.now()
        self.save(update_fields=["status", "realized_at", "updated_at"])
        return self

    def void(self):
        if self.status != self.Status.ESTIMATED:
            raise ValidationError(f"Cannot void savings in status '{self.status}'.")
        self.status = self.Status.VOID
        self.save(update_fields=["status", "updated_at"])
        return self
