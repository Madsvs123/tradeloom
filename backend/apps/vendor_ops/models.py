from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


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
    legal_name = models.CharField(max_length=180)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    country = models.CharField(max_length=2, blank=True)
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        ordering = ("name",)

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


class VendorPerformanceRecord(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="performance_records")
    period = models.CharField(max_length=32)
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    quality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    fulfillment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    metrics = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="published_performance_records"
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("vendor", "period")

    def __str__(self):
        return f"{self.vendor.name} {self.period}"


class VendorScorecard(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="scorecards")
    period = models.CharField(max_length=32)
    criteria = models.JSONField(default=list, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    band = models.CharField(max_length=16, default="bronze")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="vendor_scorecards"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="decided_vendor_scorecards"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Scorecard {self.vendor.name} {self.period}"


class VendorDocument(TimeStampedModel):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="vendor_documents")
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=80)
    file_url = models.URLField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UPLOADED)
    expires_at = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="verified_vendor_documents"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)


class PriceChangeRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    price_book_item = models.ForeignKey("PriceBookItem", on_delete=models.CASCADE, related_name="price_change_requests")
    requested_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="price_change_requests"
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="decided_price_changes"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)


class VendorAnnouncement(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=180)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="vendor_announcements"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class ServiceRating(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="service_ratings")
    order_number = models.CharField(max_length=40, blank=True)
    customer_name = models.CharField(max_length=180, blank=True)
    rating = models.PositiveSmallIntegerField(default=0)
    review = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.vendor.name} — {self.rating}/5"


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
        ordering = ("vendor", "sku")

    @property
    def available(self):
        return self.quantity_on_hand - self.quantity_reserved


class InventoryAdjustment(TimeStampedModel):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="adjustments")
    delta = models.IntegerField()
    reason = models.CharField(max_length=160, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_adjustments"
    )


class PriceBookItem(TimeStampedModel):
    vendor = models.ForeignKey(VendorAccount, on_delete=models.CASCADE, related_name="price_book_items")
    sku = models.CharField(max_length=80)
    currency = models.CharField(max_length=3, default="USD")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    min_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("vendor", "sku", "currency")
        ordering = ("vendor", "sku")


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

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("vendor", "order_number")


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

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("vendor", "rfq_reference")


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

    class Meta:
        ordering = ("-created_at",)


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
