from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VendorAccount(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_accounts")
    name = models.CharField(max_length=180)
    legal_name = models.CharField(max_length=180, blank=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    country = models.CharField(max_length=2, blank=True)
    currency = models.CharField(max_length=3, default="USD")

    def __str__(self):
        return self.name


class VendorTeamMembership(TimeStampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        OPERATOR = "operator", "Operator"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="team")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_memberships")
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.OPERATOR)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("vendor", "user")


class InventoryItem(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="inventory_items")
    sku = models.CharField(max_length=80)
    name = models.CharField(max_length=180)
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        unique_together = ("vendor", "sku")

    @property
    def available(self):
        return self.quantity_on_hand - self.quantity_reserved


class InventoryAdjustment(TimeStampedModel):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="adjustments")
    delta = models.IntegerField()
    reason = models.CharField(max_length=160, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=True, on_delete=models.SET_NULL)


class PriceBookItem(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="price_book_items")
    sku = models.CharField(max_length=80)
    currency = models.CharField(max_length=3, default="USD")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    min_quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)


class PriceBookChange(TimeStampedModel):
    item = models.ForeignKey(PriceBookItem, on_delete=models.CASCADE, related_name="changes")
    previous_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.CharField(max_length=160, blank=True)


class IncomingOrder(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        ALLOCATED = "allocated", "Allocated"
        SHIPPED = "shipped", "Shipped"
        CLOSED = "closed", "Closed"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="incoming_orders")
    order_number = models.CharField(max_length=40)
    buyer_name = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    currency = models.CharField(max_length=3, default="USD")
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    due_at = models.DateTimeField(null=True, blank=True)


class VendorRFQ(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        DRAFTING = "drafting", "Drafting"
        SUBMITTED = "submitted", "Submitted"
        LOST = "lost", "Lost"
        WON = "won", "Won"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="rfqs")
    rfq_reference = models.CharField(max_length=40)
    title = models.CharField(max_length=180)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.INVITED)
    due_at = models.DateTimeField(null=True, blank=True)
    quoted_total = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)


class CustomerRelationshipNote(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="customer_notes")
    customer_name = models.CharField(max_length=180)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class VendorPayout(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=80, blank=True)


class VendorDispute(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In review"
        RESOLVED = "resolved", "Resolved"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="disputes")
    order_number = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=180)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")


class VendorReport(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=160)
    period = models.CharField(max_length=32, blank=True)
    payload = models.JSONField(default=dict, blank=True)
