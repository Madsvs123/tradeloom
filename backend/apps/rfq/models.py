import uuid
from decimal import Decimal

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
    award_reason = models.TextField(blank=True)
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
            self.reference = f"RFQ{uuid.uuid4().hex[:10].upper()}"
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
    currency = models.CharField(max_length=3, default="USD")
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"))
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
            raise ValidationError("An attachment must be linked to an RFQ, quotation, or counteroffer.")


class RFQStatusHistory(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=24, blank=True)
    to_status = models.CharField(max_length=24)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)


class RfqTemplate(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    payment_terms = models.CharField(max_length=255, blank=True)
    delivery_location = models.CharField(max_length=255, blank=True)
    validity_days = models.PositiveIntegerField(default=30)
    line_items = models.JSONField(default=list, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="rfq_templates"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def activate(self):
        if self.status == self.Status.ARCHIVED:
            raise ValidationError("Archived templates cannot be activated.")
        if not self.line_items:
            raise ValidationError("A template must define at least one line item before activation.")
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status", "updated_at"])
        return self

    def archive(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active templates can be archived.")
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status", "updated_at"])
        return self

    def instantiate(self, buyer, title=None):
        rfq = RFQ.objects.create(
            buyer=buyer,
            title=title or self.name,
            description=self.description,
            currency=self.currency,
            payment_terms=self.payment_terms,
            delivery_location=self.delivery_location,
            validity_days=self.validity_days,
        )
        for index, line in enumerate(self.line_items, start=1):
            RFQLineItem.objects.create(
                rfq=rfq,
                line_number=index,
                sku=line.get("sku", ""),
                description=line.get("description", ""),
                quantity=Decimal(str(line.get("quantity", 1))),
                unit=line.get("unit", "each"),
                target_unit_price=line.get("target_unit_price"),
            )
        return rfq


class EvaluationCriterion(TimeStampedModel):
    class Scale(models.TextChoices):
        POINTS_10 = "points_10", "0-10 points"
        POINTS_100 = "points_100", "0-100 points"
        PASS_FAIL = "pass_fail", "Pass / Fail"

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="evaluation_criteria")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    scale = models.CharField(max_length=16, choices=Scale.choices, default=Scale.POINTS_10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("rfq", "id")

    def __str__(self):
        return f"{self.rfq.reference}: {self.name}"


class EvaluationScore(TimeStampedModel):
    criterion = models.ForeignKey(EvaluationCriterion, on_delete=models.CASCADE, related_name="scores")
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name="evaluation_scores")
    score = models.DecimalField(max_digits=6, decimal_places=2)
    passed = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    scored_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_evaluation_scores")

    class Meta:
        ordering = ("criterion", "id")
        unique_together = ("criterion", "quotation")

    def clean(self):
        if self.criterion.scale == EvaluationCriterion.Scale.PASS_FAIL and self.score not in (0, 1):
            raise ValidationError("Pass/fail criteria accept a score of 0 or 1 only.")
        if self.criterion.scale == EvaluationCriterion.Scale.POINTS_10 and not (0 <= self.score <= 10):
            raise ValidationError("Score must be between 0 and 10.")
        if self.criterion.scale == EvaluationCriterion.Scale.POINTS_100 and not (0 <= self.score <= 100):
            raise ValidationError("Score must be between 0 and 100.")


class QuotationComparisonSnapshot(TimeStampedModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="comparison_snapshots")
    snapshot = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="rfq_comparison_snapshots"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Comparison for {self.rfq.reference}"


class RfqDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        SPECIFICATION = "specification", "Specification"
        DRAWING = "drawing", "Drawing"
        TERMS = "terms", "Terms and conditions"
        APPENDIX = "appendix", "Appendix"
        OTHER = "other", "Other"

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices, default=DocumentType.OTHER)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rfq_documents"
    )

    class Meta:
        ordering = ("rfq", "title")

    def __str__(self):
        return self.title


class NegotiationRoom(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    rfq = models.OneToOneField(RFQ, on_delete=models.CASCADE, related_name="negotiation_room")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    participants = models.JSONField(default=list, blank=True)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="opened_negotiation_rooms"
    )
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Negotiation room for {self.rfq.reference}"

    def add_participant(self, user_id):
        if self.status == self.Status.CLOSED:
            raise ValidationError("Closed negotiation rooms cannot accept participants.")
        if user_id not in self.participants:
            raise ValidationError("This user is already a participant.")
        self.participants = list(self.participants) + [user_id]
        self.save(update_fields=["participants", "updated_at"])
        return self

    def close(self):
        if self.status != self.Status.OPEN:
            raise ValidationError("This negotiation room is already closed.")
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=["status", "closed_at", "updated_at"])
        return self
