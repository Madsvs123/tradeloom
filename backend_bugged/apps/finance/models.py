from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Wallet(TimeStampedModel):
    class Kind(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SUPPLIER = "supplier", "Supplier"
        PLATFORM = "platform", "Platform"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallets")
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.BUYER)
    currency = models.CharField(max_length=3, default="USD")
    available = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    held = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("owner", "kind", "currency")

    @property
    def total(self):
        return self.available + self.held


class LedgerAccount(TimeStampedModel):
    class AccountType(models.TextChoices):
        ASSET = "asset", "Asset"
        LIABILITY = "liability", "Liability"
        REVENUE = "revenue", "Revenue"
        EXPENSE = "expense", "Expense"

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    account_type = models.CharField(max_length=16, choices=AccountType.choices)
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)


class LedgerEntry(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        VOID = "void", "Void"

    debit_account = models.ForeignKey(LedgerAccount, on_delete=models.PROTECT, related_name="debits")
    credit_account = models.ForeignKey(LedgerAccount, on_delete=models.PROTECT, related_name="credits")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    memo = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class EscrowAccount(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        FUNDED = "funded", "Funded"
        RELEASED = "released", "Released"
        REFUNDED = "refunded", "Refunded"
        CLOSED = "closed", "Closed"

    order_id = models.PositiveIntegerField(null=True, blank=True)
    buyer_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="buyer_escrows")
    seller_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="seller_escrows")
    currency = models.CharField(max_length=3, default="USD")
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)


class EscrowHold(TimeStampedModel):
    class Status(models.TextChoices):
        HELD = "held", "Held"
        RELEASED = "released", "Released"
        REFUNDED = "refunded", "Refunded"

    escrow = models.ForeignKey(EscrowAccount, on_delete=models.CASCADE, related_name="holds")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.HELD)


class SettlementBatch(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        SETTLED = "settled", "Settled"

    reference = models.CharField(max_length=40, unique=True)
    currency = models.CharField(max_length=3, default="USD")
    gross_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    fee_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    net_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    settled_at = models.DateTimeField(null=True, blank=True)


class PayoutInstruction(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    settlement = models.ForeignKey(SettlementBatch, on_delete=models.CASCADE, related_name="payouts")
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="payouts")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    destination = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)


class TaxRegistration(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tax_registrations")
    jurisdiction = models.CharField(max_length=80)
    tax_id = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)


class TaxAssessment(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FILED = "filed", "Filed"

    registration = models.ForeignKey(TaxRegistration, on_delete=models.CASCADE, related_name="assessments")
    period = models.CharField(max_length=32)
    taxable_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    filed_at = models.DateTimeField(null=True, blank=True)


class CreditFacility(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CLOSED = "closed", "Closed"

    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_facilities")
    limit = models.DecimalField(max_digits=14, decimal_places=2)
    drawn = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))


class CreditDraw(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    facility = models.ForeignKey(CreditFacility, on_delete=models.CASCADE, related_name="draws")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    approved_at = models.DateTimeField(null=True, blank=True)


class ReconciliationBatch(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        MATCHED = "matched", "Matched"

    reference = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    currency = models.CharField(max_length=3, default="USD")
    expected_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    run_at = models.DateTimeField(null=True, blank=True)


class ReconciliationItem(TimeStampedModel):
    batch = models.ForeignKey(ReconciliationBatch, on_delete=models.CASCADE, related_name="items")
    reference = models.CharField(max_length=80)
    expected_amount = models.DecimalField(max_digits=14, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    matched = models.BooleanField(default=False)


class FinanceStatement(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_statements")
    period = models.CharField(max_length=32)
    currency = models.CharField(max_length=3, default="USD")
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    closing_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
