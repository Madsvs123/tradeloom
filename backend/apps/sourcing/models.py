import uuid
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


class SourcingProject(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sourcing_projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    budget = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default="USD")
    target_start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SRC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class Tender(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        AWARDED = "awarded", "Awarded"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    project = models.ForeignKey(SourcingProject, on_delete=models.CASCADE, related_name="tenders")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tenders_created")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    closing_at = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    estimated_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    award_notes = models.TextField(blank=True)
    awarded_response = models.ForeignKey(
        "TenderResponse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awarded_tenders",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SRC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class TenderLot(TimeStampedModel):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="lots")
    lot_number = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit = models.CharField(max_length=32, default="each")
    target_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        ordering = ("lot_number", "id")
        unique_together = ("tender", "lot_number")

    def __str__(self):
        return f"{self.tender.reference} - Lot {self.lot_number}"


class TenderDocument(TimeStampedModel):
    class DocType(models.TextChoices):
        SPECIFICATION = "specification", "Specification"
        TERMS = "terms", "Terms and Conditions"
        DRAWING = "drawing", "Drawing"
        BOQ = "boq", "Bill of Quantities"
        OTHER = "other", "Other"

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tender_documents"
    )
    doc_type = models.CharField(max_length=24, choices=DocType.choices, default=DocType.OTHER)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    content_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ("tender", "id")

    def __str__(self):
        return self.file_name


class BidPackage(TimeStampedModel):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        DOWNLOADED = "downloaded", "Downloaded"
        SUBMITTED = "submitted", "Submitted"
        WITHDRAWN = "withdrawn", "Withdrawn"

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="bid_packages")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bid_packages")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ISSUED)
    issued_at = models.DateTimeField(default=timezone.now)
    downloaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("tender", "id")
        unique_together = ("tender", "supplier")

    def __str__(self):
        return f"{self.tender.reference} - {self.supplier}"


class TenderResponse(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        WITHDRAWN = "withdrawn", "Withdrawn"
        UNDER_EVALUATION = "under_evaluation", "Under Evaluation"
        AWARDED = "awarded", "Awarded"
        UNSUCCESSFUL = "unsuccessful", "Unsuccessful"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="responses")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tender_responses")
    package = models.ForeignKey(BidPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    weighted_score = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("tender", "supplier")

    def __str__(self):
        return f"{self.reference} - {self.tender.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SRC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class BidLineItem(TimeStampedModel):
    response = models.ForeignKey(TenderResponse, on_delete=models.CASCADE, related_name="lines")
    lot = models.ForeignKey(TenderLot, on_delete=models.CASCADE, related_name="bid_lines")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    lead_time_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("response", "id")
        unique_together = ("response", "lot")

    def __str__(self):
        return f"{self.response.reference} - {self.lot.name}"


class EvaluationCriterion(TimeStampedModel):
    class Category(models.TextChoices):
        PRICE = "price", "Price"
        QUALITY = "quality", "Quality"
        DELIVERY = "delivery", "Delivery"
        COMPLIANCE = "compliance", "Compliance"
        SUSTAINABILITY = "sustainability", "Sustainability"
        OTHER = "other", "Other"

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=24, choices=Category.choices, default=Category.OTHER)
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("100.00"))

    class Meta:
        ordering = ("-weight", "id")

    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class BidEvaluation(TimeStampedModel):
    response = models.ForeignKey(TenderResponse, on_delete=models.CASCADE, related_name="evaluations")
    criterion = models.ForeignKey(EvaluationCriterion, on_delete=models.CASCADE, related_name="evaluations")
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bid_evaluations")
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    comments = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("response", "criterion")
        unique_together = ("response", "criterion")

    def __str__(self):
        return f"{self.response.reference} - {self.criterion.name}: {self.score}"


class ReverseAuction(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        OPEN = "open", "Open"
        PAUSED = "paused", "Paused"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="auctions", null=True, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reverse_auctions")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    currency = models.CharField(max_length=3, default="USD")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    reserve_price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    minimum_decrement = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("1.00"), validators=[MinValueValidator(0)]
    )
    current_best_bid = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    current_best_bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leading_auctions",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"SRC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class AuctionBid(TimeStampedModel):
    auction = models.ForeignKey(ReverseAuction, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="auction_bids")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    placed_at = models.DateTimeField(default=timezone.now)
    is_winning = models.BooleanField(default=False)

    class Meta:
        ordering = ("-amount", "-placed_at")

    def __str__(self):
        return f"{self.auction.reference} - {self.bidder}: {self.amount}"


class SupplierInvitation(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        WITHDRAWN = "withdrawn", "Withdrawn"

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="supplier_invitations")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tender_invitations")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tender_invitations_sent"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.INVITED)
    invited_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ("tender", "id")
        unique_together = ("tender", "supplier")

    def __str__(self):
        return f"{self.tender.reference} - {self.supplier}"
