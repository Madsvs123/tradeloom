from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MoneyFields(models.Model):
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    fee_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        abstract = True


class TaxRate(TimeStampedModel):
    name = models.CharField(max_length=120)
    jurisdiction = models.CharField(max_length=120, blank=True)
    percent = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CustomerPricing(TimeStampedModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_customer_prices")
    sku = models.CharField(max_length=128)
    currency = models.CharField(max_length=3, default="USD")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["customer", "sku", "currency", "is_active"])]


class VolumeDiscount(TimeStampedModel):
    sku = models.CharField(max_length=128, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="order_volume_discounts"
    )
    min_quantity = models.PositiveIntegerField(default=1)
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    amount_off = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)


class CreditTerm(TimeStampedModel):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_credit_terms")
    net_days = models.PositiveIntegerField(default=30)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)


class PurchasingLimit(TimeStampedModel):
    class Period(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_purchasing_limits")
    sku = models.CharField(max_length=128, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    period = models.CharField(max_length=16, choices=Period.choices, default=Period.MONTHLY)
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    max_quantity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class CommerceContract(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_contracts")
    number = models.CharField(max_length=64, unique=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    starts_at = models.DateField()
    ends_at = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True)

    def __str__(self):
        return self.number


class Cart(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CONVERTED = "converted", "Converted"
        ABANDONED = "abandoned", "Abandoned"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=128)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    supplier_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("cart", "sku")


class Order(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending approval"
        APPROVED = "approved", "Approved"
        CONFIRMED = "confirmed", "Confirmed"
        FULFILLING = "fulfilling", "Fulfilling"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        INVOICED = "invoiced", "Invoiced"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        RETURNED = "returned", "Returned"

    number = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    placed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=128)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")


class OrderStatusHistory(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=24, blank=True)
    to_status = models.CharField(max_length=24)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)


class PurchaseOrder(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        CLOSED = "closed", "Closed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="purchase_orders")
    number = models.CharField(max_length=32, unique=True)
    supplier_id = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateTimeField(null=True, blank=True)


class Approval(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="order_approvals")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)


class Invoice(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PARTIALLY_PAID = "partially_paid", "Partially paid"
        PAID = "paid", "Paid"
        VOID = "void", "Void"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="invoices")
    number = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    due_date = models.DateField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    method = models.CharField(max_length=40, default="wire")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CAPTURED)
    reference = models.CharField(max_length=80, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class Refund(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="refunds")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name="refunds")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    reason = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class Cancellation(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="cancellation")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)
    restock_items = models.BooleanField(default=False)


class ReturnRequest(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        APPROVED = "approved", "Approved"
        RECEIVED = "received", "Received"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    reason = models.TextField(blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class ReturnItem(TimeStampedModel):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="return_items")
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=160, blank=True)


class Shipment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        EXCEPTION = "exception", "Exception"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    carrier = models.CharField(max_length=80, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)


class ShipmentItem(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="shipment_items")
    quantity = models.PositiveIntegerField(default=1)


class DeliveryTrackingEvent(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="tracking_events")
    status = models.CharField(max_length=80)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)


class RecurringOrder(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recurring_orders")
    name = models.CharField(max_length=160)
    interval_days = models.PositiveIntegerField(default=30)
    next_run_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    template = models.JSONField(default=dict, blank=True)


class ReorderList(TimeStampedModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reorder_lists")
    name = models.CharField(max_length=160)


class ReorderListItem(TimeStampedModel):
    reorder_list = models.ForeignKey(ReorderList, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=128)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)


class Commission(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="commissions")
    vendor_id = models.PositiveIntegerField(null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")


class MarketplaceFee(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="marketplace_fees")
    name = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")


class Settlement(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        SETTLED = "settled", "Settled"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="settlements")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    settled_at = models.DateTimeField(null=True, blank=True)


class Payout(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    destination = models.CharField(max_length=160, blank=True)


class LedgerTransaction(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    kind = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    reference = models.CharField(max_length=80, blank=True)


class BlanketOrder(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blanket_orders")
    contract = models.ForeignKey(
        CommerceContract, null=True, blank=True, on_delete=models.SET_NULL, related_name="blanket_orders"
    )
    number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    title = models.CharField(max_length=180)
    supplier_id = models.PositiveIntegerField(null=True, blank=True)
    total_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    fulfilled_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"BLK-{uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def activate(self):
        if self.status != self.Status.DRAFT:
            raise ValidationError(f"Cannot activate a blanket order in status '{self.status}'.")
        if self.total_quantity == 0:
            raise ValidationError("A blanket order must have a positive total quantity.")
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status", "updated_at"])
        return self

    def complete(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active blanket orders can be completed.")
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])
        return self

    def cancel(self):
        if self.status in (self.Status.COMPLETED, self.Status.CANCELLED):
            raise ValidationError("This blanket order can no longer be cancelled.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
        return self


class BlanketOrderRelease(TimeStampedModel):
    blanket_order = models.ForeignKey(BlanketOrder, on_delete=models.CASCADE, related_name="releases")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="blanket_release")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    released_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("released_at",)

    def __str__(self):
        return f"Release {self.pk} against {self.blanket_order.number}"


class DeliverySchedule(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        CONFIRMED = "confirmed", "Confirmed"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        SKIPPED = "skipped", "Skipped"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="delivery_schedules")
    sequence = models.PositiveIntegerField(default=1)
    scheduled_date = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    delivered_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PLANNED)
    shipment = models.ForeignKey(Shipment, null=True, blank=True, on_delete=models.SET_NULL, related_name="schedules")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("order", "sequence")
        unique_together = ("order", "sequence")

    def __str__(self):
        return f"{self.order.number} #{self.sequence}"


class OrderMilestone(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACHIEVED = "achieved", "Achieved"
        SKIPPED = "skipped", "Skipped"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    achieved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ("order", "due_at", "id")

    def __str__(self):
        return f"{self.order.number}: {self.title}"

    def achieve(self):
        if self.status != self.Status.PENDING:
            raise ValidationError(f"Cannot achieve a milestone in status '{self.status}'.")
        self.status = self.Status.ACHIEVED
        self.achieved_at = timezone.now()
        self.save(update_fields=["status", "achieved_at", "updated_at"])
        return self

    def skip(self):
        if self.status != self.Status.PENDING:
            raise ValidationError(f"Cannot skip a milestone in status '{self.status}'.")
        self.status = self.Status.SKIPPED
        self.save(update_fields=["status", "updated_at"])
        return self


class Backorder(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="backorders")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="backorders")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    fulfilled_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    expected_restock_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Backorder {self.pk} for {self.order.number}"


class CreditMemo(TimeStampedModel, MoneyFields):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        VOID = "void", "Void"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="credit_memos")
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="credit_memos")
    number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    reason = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"CM-{uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def issue(self):
        if self.status != self.Status.DRAFT:
            raise ValidationError(f"Cannot issue a credit memo in status '{self.status}'.")
        if self.total <= 0:
            raise ValidationError("A credit memo must have a positive total.")
        self.status = self.Status.ISSUED
        self.issued_at = timezone.now()
        self.save(update_fields=["status", "issued_at", "updated_at"])
        return self

    def apply(self):
        if self.status != self.Status.ISSUED:
            raise ValidationError("Only issued credit memos can be applied.")
        self.status = self.Status.APPLIED
        self.applied_at = timezone.now()
        self.save(update_fields=["status", "applied_at", "updated_at"])
        return self

    def void(self):
        if self.status in (self.Status.APPLIED, self.Status.VOID):
            raise ValidationError("This credit memo can no longer be voided.")
        self.status = self.Status.VOID
        self.save(update_fields=["status", "updated_at"])
        return self


class OrderHold(TimeStampedModel):
    class Reason(models.TextChoices):
        CREDIT_CHECK = "credit_check", "Credit check"
        FRAUD_REVIEW = "fraud_review", "Fraud review"
        DOCUMENTATION = "documentation", "Documentation"
        SUPPLIER_CONFIRMATION = "supplier_confirmation", "Supplier confirmation"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RELEASED = "released", "Released"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="holds")
    reason = models.CharField(max_length=40, choices=Reason.choices, default=Reason.OTHER)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    placed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="placed_order_holds"
    )
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="released_order_holds"
    )
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Hold on {self.order.number}: {self.reason}"

    def release(self, user):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active holds can be released.")
        self.status = self.Status.RELEASED
        self.released_by = user
        self.released_at = timezone.now()
        self.save(update_fields=["status", "released_by", "released_at", "updated_at"])
        return self


class PackingSlip(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="packing_slips")
    number = models.CharField(max_length=32, unique=True, editable=False)
    items = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="generated_packing_slips"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"PS-{uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
