import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContractTemplate(TimeStampedModel):
    name = models.CharField(max_length=180)
    category = models.CharField(max_length=80, blank=True)
    body = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class LegalContract(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ACTIVE = "active", "Active"
        AMENDED = "amended", "Amended"
        RENEWED = "renewed", "Renewed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    template = models.ForeignKey(ContractTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name="agreements")
    number = models.CharField(max_length=40, unique=False, editable=False)
    title = models.CharField(max_length=180)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="buyer_contracts"
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplier_contracts"
    )
    currency = models.CharField(max_length=3, default="USD")
    total = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT, db_index=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    body = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number or self.title

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"CTR-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class ContractClause(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="clauses")
    heading = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=1)


class Amendment(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPLIED = "applied", "Applied"
        REJECTED = "rejected", "Rejected"

    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="amendments")
    summary = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    effective_on = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class Obligation(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="obligations")
    description = models.CharField(max_length=255)
    due_at = models.DateTimeField(null=True, blank=True)
    fulfilled = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class RenewalTerm(TimeStampedModel):
    contract = models.ForeignKey(LegalContract, on_delete=models.CASCADE, related_name="renewal_terms")
    notice_days = models.PositiveIntegerField(default=30)
    auto_renew = models.BooleanField(default=False)
    term_months = models.PositiveIntegerField(default=12)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
