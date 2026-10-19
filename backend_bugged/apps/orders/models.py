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
    quantity = models.PositiveIntegerField(default=1)
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
    restock_items = models.BooleanField(default=True)


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
