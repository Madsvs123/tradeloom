import uuid

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    AdvancedShippingNotice,
    DeliveryAppointment,
    HazardousDeclaration,
    InventoryCount,
    LogisticsException,
    PackingList,
    RateTable,
    ReceivingInspection,
    ShipmentDocument,
    ShipmentPlan,
    TrackingEvent,
)

PLAN_TRANSITIONS = {
    ShipmentPlan.Status.DRAFT: {ShipmentPlan.Status.PLANNED, ShipmentPlan.Status.CANCELLED},
    ShipmentPlan.Status.PLANNED: {ShipmentPlan.Status.IN_TRANSIT, ShipmentPlan.Status.CANCELLED},
    ShipmentPlan.Status.IN_TRANSIT: {ShipmentPlan.Status.DELIVERED},
    ShipmentPlan.Status.DELIVERED: set(),
    ShipmentPlan.Status.CANCELLED: set(),
}

APPOINTMENT_TRANSITIONS = {
    DeliveryAppointment.Status.REQUESTED: {
        DeliveryAppointment.Status.CONFIRMED,
        DeliveryAppointment.Status.MISSED,
        DeliveryAppointment.Status.COMPLETED,
    },
    DeliveryAppointment.Status.CONFIRMED: {DeliveryAppointment.Status.COMPLETED, DeliveryAppointment.Status.MISSED},
    DeliveryAppointment.Status.COMPLETED: set(),
    DeliveryAppointment.Status.MISSED: set(),
}

INSPECTION_TRANSITIONS = {
    ReceivingInspection.Status.PENDING: {ReceivingInspection.Status.PASSED, ReceivingInspection.Status.FAILED},
    ReceivingInspection.Status.PASSED: set(),
    ReceivingInspection.Status.FAILED: set(),
}

RATE_TABLE_TRANSITIONS = {
    RateTable.Status.DRAFT: {RateTable.Status.ACTIVE, RateTable.Status.ARCHIVED},
    RateTable.Status.ACTIVE: {RateTable.Status.ARCHIVED},
    RateTable.Status.ARCHIVED: set(),
}

INVENTORY_COUNT_TRANSITIONS = {
    InventoryCount.Status.DRAFT: {InventoryCount.Status.COUNTED},
    InventoryCount.Status.COUNTED: {InventoryCount.Status.RECONCILED},
    InventoryCount.Status.RECONCILED: set(),
}

SHIPMENT_DOCUMENT_TRANSITIONS = {
    ShipmentDocument.Status.UPLOADED: {ShipmentDocument.Status.VERIFIED, ShipmentDocument.Status.REJECTED},
    ShipmentDocument.Status.VERIFIED: set(),
    ShipmentDocument.Status.REJECTED: set(),
}

DECLARATION_TRANSITIONS = {
    HazardousDeclaration.Status.PENDING: {HazardousDeclaration.Status.APPROVED, HazardousDeclaration.Status.REJECTED},
    HazardousDeclaration.Status.APPROVED: set(),
    HazardousDeclaration.Status.REJECTED: set(),
}


def _ref(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def _assert_transition(current, target, transitions):
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move from status '{current}' to '{target}'.")


def add_tracking_event(plan, status, location="", description="", occurred_at=None):
    if not status:
        raise ValidationError("Tracking status is required.")
    event = TrackingEvent.objects.create(
        shipment_plan=plan,
        status=status,
        location=location,
        description=description,
        occurred_at=occurred_at or timezone.now(),
    )
    mapping = {
        "picked_up": ShipmentPlan.Status.IN_TRANSIT,
        "in_transit": ShipmentPlan.Status.IN_TRANSIT,
        "delivered": ShipmentPlan.Status.DELIVERED,
    }
    target = mapping.get(status)
    if target and plan.status != target:
        allowed = PLAN_TRANSITIONS.get(plan.status, set())
        if target in allowed:
            plan.status = target
            plan.save(update_fields=["status", "updated_at"])
    return event


def create_packing_list(plan, package_count=0, gross_weight_kg=0, notes=""):
    if plan.status == ShipmentPlan.Status.CANCELLED:
        raise ValidationError("Cannot pack a cancelled shipment plan.")
    packing = PackingList.objects.create(
        shipment_plan=plan,
        number=_ref("PL"),
        package_count=package_count,
        gross_weight_kg=gross_weight_kg,
        notes=notes,
    )
    if plan.status == ShipmentPlan.Status.DRAFT:
        plan.status = ShipmentPlan.Status.PLANNED
        plan.save(update_fields=["status", "updated_at"])
    return packing


def send_asn(asn):
    if asn.status != AdvancedShippingNotice.Status.DRAFT:
        raise ValidationError("Only draft ASNs can be sent.")
    if not asn.shipment_plan.packing_lists.exists():
        raise ValidationError("Create a packing list before sending an ASN.")
    asn.status = AdvancedShippingNotice.Status.SENT
    asn.sent_at = timezone.now()
    asn.payload = {
        "plan_id": asn.shipment_plan_id,
        "origin": asn.shipment_plan.origin,
        "destination": asn.shipment_plan.destination,
    }
    asn.save(update_fields=["status", "sent_at", "payload", "updated_at"])
    return asn


def confirm_appointment(appointment):
    _assert_transition(appointment.status, DeliveryAppointment.Status.CONFIRMED, APPOINTMENT_TRANSITIONS)
    appointment.status = DeliveryAppointment.Status.CONFIRMED
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


def complete_appointment(appointment):
    _assert_transition(appointment.status, DeliveryAppointment.Status.COMPLETED, APPOINTMENT_TRANSITIONS)
    appointment.status = DeliveryAppointment.Status.COMPLETED
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


def miss_appointment(appointment):
    _assert_transition(appointment.status, DeliveryAppointment.Status.MISSED, APPOINTMENT_TRANSITIONS)
    appointment.status = DeliveryAppointment.Status.MISSED
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


def pass_inspection(inspection, notes=""):
    _assert_transition(inspection.status, ReceivingInspection.Status.PASSED, INSPECTION_TRANSITIONS)
    inspection.status = ReceivingInspection.Status.PASSED
    inspection.notes = notes or inspection.notes
    inspection.save(update_fields=["status", "notes", "updated_at"])
    return inspection


def fail_inspection(inspection, notes=""):
    _assert_transition(inspection.status, ReceivingInspection.Status.FAILED, INSPECTION_TRANSITIONS)
    if not notes:
        raise ValidationError("A failure note is required.")
    inspection.status = ReceivingInspection.Status.FAILED
    inspection.notes = notes
    inspection.save(update_fields=["status", "notes", "updated_at"])
    return inspection


def activate_rate_table(rate_table):
    _assert_transition(rate_table.status, RateTable.Status.ACTIVE, RATE_TABLE_TRANSITIONS)
    if rate_table.base_rate <= 0:
        raise ValidationError("A rate table must have a positive base rate.")
    rate_table.status = RateTable.Status.ACTIVE
    rate_table.save(update_fields=["status", "updated_at"])
    return rate_table


def archive_rate_table(rate_table):
    _assert_transition(rate_table.status, RateTable.Status.ARCHIVED, RATE_TABLE_TRANSITIONS)
    rate_table.status = RateTable.Status.ARCHIVED
    rate_table.save(update_fields=["status", "updated_at"])
    return rate_table


def start_inventory_count(inventory_count, actor=None):
    _assert_transition(inventory_count.status, InventoryCount.Status.COUNTED, INVENTORY_COUNT_TRANSITIONS)
    if not inventory_count.items:
        raise ValidationError("Record counted items before completing the count.")
    inventory_count.status = InventoryCount.Status.COUNTED
    inventory_count.counted_at = timezone.now()
    inventory_count.counted_by = actor
    inventory_count.save(update_fields=["status", "counted_at", "counted_by", "updated_at"])
    return inventory_count


def reconcile_inventory_count(inventory_count):
    _assert_transition(inventory_count.status, InventoryCount.Status.RECONCILED, INVENTORY_COUNT_TRANSITIONS)
    reconciled_items = []
    net_variance = Decimal("0.00")
    for item in inventory_count.items:
        expected = Decimal(str(item.get("expected_qty") or 0))
        counted = Decimal(str(item.get("counted_qty") or 0))
        variance = expected - counted
        net_variance += variance
        reconciled_items.append(
            {
                "sku": item.get("sku", ""),
                "expected_qty": str(expected),
                "counted_qty": str(counted),
                "variance": str(variance),
            }
        )
    inventory_count.status = InventoryCount.Status.RECONCILED
    inventory_count.reconciled_at = timezone.now()
    inventory_count.items = reconciled_items
    inventory_count.notes = (inventory_count.notes + "\n" if inventory_count.notes else "") + (
        f"Reconciled {len(reconciled_items)} lines; net variance {str(net_variance)}."
    )
    inventory_count.save(update_fields=["status", "reconciled_at", "items", "notes", "updated_at"])
    return inventory_count


def verify_shipment_document(document, reviewer=None, accept=True, notes=""):
    _assert_transition(document.status, ShipmentDocument.Status.VERIFIED, SHIPMENT_DOCUMENT_TRANSITIONS)
    if accept:
        document.status = ShipmentDocument.Status.VERIFIED
    else:
        if not notes:
            raise ValidationError("A note is required to reject a shipment document.")
        document.status = ShipmentDocument.Status.REJECTED
    document.verified_by = reviewer
    document.verified_at = timezone.now()
    document.notes = notes or document.notes
    document.save(update_fields=["status", "verified_by", "verified_at", "notes", "updated_at"])
    return document


def approve_hazardous_declaration(declaration, actor=None, notes=""):
    _assert_transition(declaration.status, HazardousDeclaration.Status.APPROVED, DECLARATION_TRANSITIONS)
    declaration.status = HazardousDeclaration.Status.APPROVED
    declaration.decided_by = actor
    declaration.decided_at = timezone.now()
    declaration.notes = notes or declaration.notes
    declaration.save(update_fields=["status", "decided_by", "decided_at", "notes", "updated_at"])
    return declaration


def reject_hazardous_declaration(declaration, actor=None, notes=""):
    _assert_transition(declaration.status, HazardousDeclaration.Status.REJECTED, DECLARATION_TRANSITIONS)
    if not notes:
        raise ValidationError("A rejection note is required.")
    declaration.status = HazardousDeclaration.Status.REJECTED
    declaration.decided_by = actor
    declaration.decided_at = timezone.now()
    declaration.notes = notes
    declaration.save(update_fields=["status", "decided_by", "decided_at", "notes", "updated_at"])
    return declaration


def resolve_exception(exception, resolution=""):
    if exception.status == LogisticsException.Status.RESOLVED:
        raise ValidationError("Exception is already resolved.")
    if not resolution:
        raise ValidationError("A resolution note is required.")
    exception.status = LogisticsException.Status.RESOLVED
    exception.resolution = resolution
    exception.resolved_at = timezone.now()
    exception.save(update_fields=["status", "resolution", "resolved_at", "updated_at"])
    return exception
