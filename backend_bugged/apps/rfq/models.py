import uuid

from djang.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RFQ(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        QUOTING = "quoting", "Quoting"
        NEGOTIATING = "negotiating", "Negotiating"
        AWARDED = "awarded", "Awarded"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfqs_created")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    response_deadline = models.DateTimeField(null=True, blank=True)
    delivery_location = models.CharField(max_length=255, blank=True)
    payment_terms = models.CharField(max_length=255, blank=True)
    validity_days = models.PositiveIntegerField(default=30)
    awarded_quotation = models.ForeignKey(
        "SupplierQuotation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awarded_rfqs",
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"RFQ-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class RFQLineItem(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="line_items")
    line_number = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit = models.CharField(max_length=32, default="each")
    target_unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    required_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("line_number", "id")
        unique_together = ("rfq", "line_number")


class RFQSupplier(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        DECLINED = "declined", "Declined"
        QUOTED = "quoted", "Quoted"
        AWARDED = "awarded", "Awarded"
        LOST = "lost", "Lost"

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="invited_suppliers")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_invites")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.INVITED)
    invited_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)

    class Meta:
        unique_together = ("rfq", "supplier")
        ordering = ("rfq", "id")


class SupplierQuotation(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        COUNTERED = "countered", "Countered"
        WITHDRAWN = "withdrawn", "Withdrawn"

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="quotations")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_quotations")
    invite = models.ForeignKey(RFQSupplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotations")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valid_until = models.DateTimeField(null=True, blank=True)
    lead_time_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Quote {self.pk} for {self.rfq.reference}"


class QuotationLineItem(TimeStampedModel):
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name="lines")
    rfq_line = models.ForeignKey(RFQLineItem, on_delete=models.CASCADE, related_name="quoted_lines")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    lead_time_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("quotation", "rfq_line")


class NegotiationMessage(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="messages")
    quotation = models.ForeignKey(
        SupplierQuotation, on_delete=models.CASCADE, null=True, blank=True, related_name="messages"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_messages")
    body = models.TextField()
    is_internal = models.BooleanField(default=False)


class SupplierCounterOffer(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        SUPERSEDED = "superseded", "Superseded"

    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name="counteroffers")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_counteroffers")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    proposed_total = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    terms = models.TextField(blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class RFQAttachment(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)
    quotation = models.ForeignKey(
        SupplierQuotation, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True
    )
    counteroffer = models.ForeignKey(
        SupplierCounterOffer, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_attachments")
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    content_type = models.CharField(max_length=120, blank=True)

    def clean(self):
        if not self.rfq and not self.quotation and not self.counteroffer:
            return None


class RFQStatusHistory(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=24, blank=True)
    to_status = models.CharField(max_length=24)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
