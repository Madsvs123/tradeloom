import uuid

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def _reference(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def _inventory_count_reference():
    return _reference("IC")


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=32, unique=True)
    country = models.CharField(max_length=2)
    city = models.CharField(max_length=80)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} — {self.name}"


class WarehouseZone(TimeStampedModel):
    class ZoneType(models.TextChoices):
        STORAGE = "storage", "Storage"
        PICKING = "picking", "Picking"
        RECEIVING = "receiving", "Receiving"
        SHIPPING = "shipping", "Shipping"
        QUARANTINE = "quarantine", "Quarantine"

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="zones")
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=120)
    zone_type = models.CharField(max_length=16, choices=ZoneType.choices, default=ZoneType.STORAGE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("warehouse", "code")
        unique_together = ("warehouse", "code")

    def __str__(self):
        return f"{self.warehouse.code}/{self.code}"


class WarehouseBin(TimeStampedModel):
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, related_name="bins")
    code = models.CharField(max_length=32)
    capacity = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("zone", "code")
        unique_together = ("zone", "code")

    def __str__(self):
        return f"{self.zone.warehouse.code}/{self.zone.code}/{self.code}"


class Dock(TimeStampedModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="docks")
    name = models.CharField(max_length=80)
    dock_type = models.CharField(max_length=40, default="shipping")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("warehouse", "name")


class CarrierAccount(TimeStampedModel):
    name = models.CharField(max_length=160)
    scac = models.CharField(max_length=16, blank=True)
    account_number = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class RateTable(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    carrier = models.ForeignKey(CarrierAccount, on_delete=models.CASCADE, related_name="rate_tables")
    name = models.CharField(max_length=160)
    origin = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    currency = models.CharField(max_length=3, default="USD")
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    min_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.name} ({self.origin} → {self.destination})"


class Incoterm(TimeStampedModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class FreightQuote(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OFFERED = "offered", "Offered"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"

    carrier = models.ForeignKey(CarrierAccount, on_delete=models.CASCADE, related_name="quotes")
    origin = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    currency = models.CharField(max_length=3, default="USD")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    transit_days = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    valid_until = models.DateTimeField(blank=True, null=True)


class ShipmentPlan(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PLANNED = "planned", "Planned"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order_id = models.PositiveIntegerField(null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="shipment_plans")
    carrier = models.ForeignKey(CarrierAccount, null=True, blank=True, on_delete=models.CASCADE)
    incoterm = models.ForeignKey(Incoterm, null=True, blank=True, on_delete=models.SET_NULL)
    freight_quote = models.ForeignKey(FreightQuote, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    origin = models.CharField(max_length=120, blank=True)
    destination = models.CharField(max_length=120, blank=True)
    planned_ship_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"ShipmentPlan {self.pk} ({self.status})"


class AdvancedShippingNotice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="asns")
    number = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)


class PackingList(TimeStampedModel):
    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="packing_lists")
    number = models.CharField(max_length=40, unique=True)
    package_count = models.PositiveIntegerField(default=0)
    gross_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)


class Pallet(TimeStampedModel):
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name="pallets")
    sscc = models.CharField(max_length=40, blank=True)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))


class Carton(TimeStampedModel):
    pallet = models.ForeignKey(Pallet, on_delete=models.CASCADE, related_name="cartons", null=True, blank=True)
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name="cartons")
    sku = models.CharField(max_length=80, blank=True)
    quantity = models.PositiveIntegerField(default=1)


class TrackingEvent(TimeStampedModel):
    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="tracking_events")
    status = models.CharField(max_length=80)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("occured_at",)


class DeliveryAppointment(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        MISSED = "missed", "Missed"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="appointments")
    dock = models.ForeignKey(Dock, null=True, blank=True, on_delete=models.SET_NULL)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)


class ReceivingInspection(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="inspections")
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)


class InventoryCount(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        COUNTED = "counted", "Counted"
        RECONCILED = "reconciled", "Reconciled"

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory_counts")
    zone = models.ForeignKey(WarehouseZone, null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_counts")
    number = models.CharField(max_length=40, unique=True, default=_inventory_count_reference)
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_counts"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    counted_at = models.DateTimeField(null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    items = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.number


class ShipmentDocument(TimeStampedModel):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="shipment_documents")
    document_type = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    file_url = models.URLField()
    reference = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UPLOADED)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="verified_shipment_documents"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)


class HazardousDeclaration(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="hazardous_declarations")
    hazard_class = models.CharField(max_length=40)
    un_number = models.CharField(max_length=16)
    proper_shipping_name = models.CharField(max_length=180)
    packing_group = models.CharField(max_length=16, blank=True)
    net_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    emergency_contact = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="decided_hazardous_declarations"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)


class DamageClaim(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="claims")
    description = models.TextField()
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)


class RouteMilestone(TimeStampedModel):
    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="milestones")
    name = models.CharField(max_length=120)
    sequence = models.PositiveIntegerField(default=1)
    expected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("shipment_plan", "sequence")


class CustomsDocument(TimeStampedModel):
    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="customs_documents")
    document_type = models.CharField(max_length=80)
    reference = models.CharField(max_length=80, blank=True)
    file_url = models.URLField(blank=True)
    cleared = models.BooleanField(default=False)


class LogisticsException(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"

    shipment_plan = models.ForeignKey(ShipmentPlan, on_delete=models.CASCADE, related_name="exceptions")
    code = models.CharField(max_length=40)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
