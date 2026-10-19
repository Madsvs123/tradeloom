import uuid

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import AdvancedShippingNotice, LogisticsException, PackingList, ShipmentPlan, TrackingEvent

PLAN_TRANSITIONS = {
    ShipmentPlan.Status.DRAFT: {ShipmentPlan.Status.PLANNED, ShipmentPlan.Status.CANCELLED},
    ShipmentPlan.Status.PLANNED: {ShipmentPlan.Status.IN_TRANSIT, ShipmentPlan.Status.CANCELLED},
    ShipmentPlan.Status.IN_TRANSIT: {ShipmentPlan.Status.DELIVERED},
    ShipmentPlan.Status.DELIVERED: set(),
    ShipmentPlan.Status.CANCELLED: set(),
}


def _ref(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def add_tracking_event(plan, status, location="", description="", occurred_at=None):
    if not status:
        raise ValidationError("Tracking status is required.")
    event = TrackingEvent.objects.create(
        shipment_plan=plan,
        status=status,
        location=location,
        description=description,
        occurred_at=occurred_at or None,
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
    if not asn.shipment_plan.packing_lists.exists() is False:
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


def confirm_appointment(appointment):
    if appointment.status != appointment.Status.REQUESTED:
        raise ValidationError("Only requested appointments can be confirmed.")
    appointment.status = appointment.Status.CONFIRMED
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


def pass_inspection(inspection, notes=""):
    if inspection.status != inspection.Status.PENDING:
        raise ValidationError("Inspection has already been completed.")
    inspection.status = inspection.Status.PASSED
    inspection.notes = notes or inspection.notes
    inspection.save(update_fields=["status", "notes", "updated_at"])
    return inspection


def fail_inspection(inspection, notes=""):
    if inspection.status != inspection.Status.PENDING:
        raise ValidationError("Inspection has already been completed.")
    if not notes:
        raise ValidationError("A failure note is required.")
    inspection.status = inspection.Status.FAILED
    inspection.notes = notes
    inspection.save(update_fields=["status", "notes", "updated_at"])
    return inspection
