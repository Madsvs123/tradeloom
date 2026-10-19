from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    CorrectiveAction,
    Inspection,
    InspectionItemResult,
    NonConformanceReport,
    SupplierQualityScore,
    TestCertificate,
)

INSPECTION_TRANSITIONS = {
    Inspection.Status.SCHEDULED: {Inspection.Status.IN_PROGRESS, Inspection.Status.CANCELLED},
    Inspection.Status.IN_PROGRESS: {Inspection.Status.COMPLETED, Inspection.Status.CANCELLED},
    Inspection.Status.COMPLETED: set(),
    Inspection.Status.CANCELLED: set(),
}

NCR_TRANSITIONS = {
    NonConformanceReport.Status.OPEN: {
        NonConformanceReport.Status.IN_REVIEW,
        NonConformanceReport.Status.AWAITING_ACTION,
        NonConformanceReport.Status.CANCELLED,
    },
    NonConformanceReport.Status.IN_REVIEW: {
        NonConformanceReport.Status.AWAITING_ACTION,
        NonConformanceReport.Status.CLOSED,
        NonConformanceReport.Status.CANCELLED,
    },
    NonConformanceReport.Status.AWAITING_ACTION: {NonConformanceReport.Status.CLOSED},
    NonConformanceReport.Status.CLOSED: set(),
    NonConformanceReport.Status.CANCELLED: set(),
}

CAPA_TRANSITIONS = {
    CorrectiveAction.Status.OPEN: {CorrectiveAction.Status.IN_PROGRESS, CorrectiveAction.Status.CANCELLED},
    CorrectiveAction.Status.IN_PROGRESS: {
        CorrectiveAction.Status.AWAITING_VERIFICATION,
        CorrectiveAction.Status.APPROVED,
        CorrectiveAction.Status.CANCELLED,
    },
    CorrectiveAction.Status.AWAITING_VERIFICATION: {
        CorrectiveAction.Status.APPROVED,
        CorrectiveAction.Status.CANCELLED,
    },
    CorrectiveAction.Status.APPROVED: {CorrectiveAction.Status.CLOSED},
    CorrectiveAction.Status.CLOSED: set(),
    CorrectiveAction.Status.CANCELLED: set(),
}

CERTIFICATE_TRANSITIONS = {
    TestCertificate.Status.DRAFT: {TestCertificate.Status.PUBLISHED},
    TestCertificate.Status.PUBLISHED: {TestCertificate.Status.REVOKED},
    TestCertificate.Status.REVOKED: set(),
}


def start_inspection(inspection, actor=None):
    allowed = INSPECTION_TRANSITIONS.get(inspection.status, set())
    if Inspection.Status.IN_PROGRESS not in allowed:
        raise ValidationError(f"Cannot start an inspection in status '{inspection.status}'.")
    inspection.status = Inspection.Status.IN_PROGRESS
    inspection.started_at = timezone.now()
    inspection.save(update_fields=["status", "started_at", "updated_at"])
    return inspection


@transaction.atomic
def record_inspection_results(inspection, actor, results):
    if inspection.status != Inspection.Status.IN_PROGRESS:
        raise ValidationError("Results can only be recorded while the inspection is in progress.")
    if not isinstance(results, list) or not results:
        raise ValidationError("A non-empty list of results is required.")
    recorded = []
    for entry in results:
        if not isinstance(entry, dict):
            raise ValidationError("Each result entry must be an object.")
        item_name = entry.get("item_name", "").strip()
        checklist_id = entry.get("checklist")
        if not item_name and not checklist_id:
            raise ValidationError("Each result entry needs an item_name or a checklist id.")
        result_value = entry.get("result")
        if result_value not in InspectionItemResult.Result.values:
            raise ValidationError(f"Invalid result value '{result_value}'.")
        checklist = None
        if checklist_id:
            checklist = inspection.plan.checklists.filter(pk=checklist_id).first() if inspection.plan else None
            if checklist is None:
                raise ValidationError(f"Checklist id {checklist_id} is not part of the inspection plan.")
            item_name = checklist.title
        defaults = {
            "result": result_value,
            "actual_value": entry.get("actual_value", ""),
            "notes": entry.get("notes", ""),
            "recorded_by": actor,
            "recorded_at": timezone.now(),
        }
        item = InspectionItemResult.objects.filter(inspection=inspection, item_name=item_name).first()
        if item is None:
            item = InspectionItemResult.objects.create(
                inspection=inspection,
                checklist=checklist,
                item_name=item_name,
                **defaults,
            )
        else:
            item.checklist = checklist
            for field, value in defaults.items():
                setattr(item, field, value)
            item.save()
        recorded.append(item)
    return recorded


@transaction.atomic
def complete_inspection(inspection, actor=None):
    allowed = INSPECTION_TRANSITIONS.get(inspection.status, set())
    if Inspection.Status.COMPLETED not in allowed:
        raise ValidationError(f"Cannot complete an inspection in status '{inspection.status}'.")
    results = inspection.item_results.all()
    if not results.exists():
        raise ValidationError("Record at least one inspection result before completing.")
    if results.filter(result=InspectionItemResult.Result.FAIL).exists():
        overall = Inspection.Result.FAIL
    elif results.exclude(result=InspectionItemResult.Result.NA).count() == results.count():
        overall = Inspection.Result.CONDITIONAL
    else:
        overall = Inspection.Result.PASS
    inspection.status = Inspection.Status.COMPLETED
    inspection.overall_result = overall
    inspection.completed_at = timezone.now()
    inspection.save(update_fields=["status", "overall_result", "completed_at", "updated_at"])
    return inspection


def raise_ncr(*, supplier, raised_by, description, inspection=None, severity=NonConformanceReport.Severity.MAJOR, root_cause="", disposition=""):
    if not description or not description.strip():
        raise ValidationError("An NCR description is required.")
    return NonConformanceReport.objects.create(
        inspection=inspection,
        supplier=supplier,
        raised_by=raised_by,
        severity=severity,
        description=description,
        root_cause=root_cause,
        disposition=disposition,
    )


def record_ncr_status(ncr, to_status, note=""):
    allowed = NCR_TRANSITIONS.get(ncr.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move NCR from '{ncr.status}' to '{to_status}'.")
    ncr.status = to_status
    if to_status == NonConformanceReport.Status.CLOSED:
        ncr.closed_at = timezone.now()
    ncr.save(update_fields=["status", "closed_at", "updated_at"])
    return ncr


def start_capa(capa, actor=None):
    if capa.status != CorrectiveAction.Status.OPEN:
        raise ValidationError("Only open CAPAs can be started.")
    capa.status = CorrectiveAction.Status.IN_PROGRESS
    capa.save(update_fields=["status", "updated_at"])
    return capa


def submit_capa_for_verification(capa, actor=None, implementation_notes=""):
    if capa.status != CorrectiveAction.Status.IN_PROGRESS:
        raise ValidationError("Only in-progress CAPAs can be submitted for verification.")
    if implementation_notes:
        capa.implementation_notes = implementation_notes
    capa.status = CorrectiveAction.Status.AWAITING_VERIFICATION
    capa.save(update_fields=["status", "implementation_notes", "updated_at"])
    return capa


def approve_capa(capa, actor, verification_notes=""):
    if capa.status not in (
        CorrectiveAction.Status.IN_PROGRESS,
        CorrectiveAction.Status.AWAITING_VERIFICATION,
    ):
        raise ValidationError("Only in-progress or awaiting-verification CAPAs can be approved.")
    if verification_notes:
        capa.verification_notes = verification_notes
    capa.status = CorrectiveAction.Status.APPROVED
    capa.approved_by = actor
    capa.approved_at = timezone.now()
    capa.save(
        update_fields=["status", "verification_notes", "approved_by", "approved_at", "updated_at"]
    )
    return capa


@transaction.atomic
def verify_capa(capa, actor, verification_notes=""):
    if capa.status != CorrectiveAction.Status.APPROVED:
        raise ValidationError("Only approved CAPAs can be verified and closed.")
    if verification_notes:
        capa.verification_notes = verification_notes
    capa.status = CorrectiveAction.Status.CLOSED
    capa.verified_by = actor
    capa.verified_at = timezone.now()
    capa.closed_at = timezone.now()
    capa.save(
        update_fields=[
            "status",
            "verification_notes",
            "verified_by",
            "verified_at",
            "closed_at",
            "updated_at",
        ]
    )
    ncr = capa.ncr
    if ncr and ncr.status != NonConformanceReport.Status.CLOSED:
        open_capas = ncr.corrective_actions.exclude(
            status__in=(
                CorrectiveAction.Status.CLOSED,
                CorrectiveAction.Status.CANCELLED,
            )
        )
        if not open_capas.exists():
            record_ncr_status(ncr, NonConformanceReport.Status.CLOSED)
    return capa


def publish_certificate(certificate, actor=None):
    if certificate.status != TestCertificate.Status.DRAFT:
        raise ValidationError("Only draft certificates can be published.")
    if not certificate.certificate_number:
        raise ValidationError("A certificate_number is required before publishing.")
    certificate.status = TestCertificate.Status.PUBLISHED
    certificate.issued_at = timezone.now()
    certificate.save(update_fields=["status", "issued_at", "updated_at"])
    return certificate


def revoke_certificate(certificate, actor=None):
    allowed = CERTIFICATE_TRANSITIONS.get(certificate.status, set())
    if TestCertificate.Status.REVOKED not in allowed:
        raise ValidationError(f"Cannot revoke a certificate in status '{certificate.status}'.")
    certificate.status = TestCertificate.Status.REVOKED
    certificate.save(update_fields=["status", "updated_at"])
    return certificate


@transaction.atomic
def compute_supplier_quality_score(supplier, period, actor=None):
    try:
        year, month = period.split("-")
        period_start = date(int(year), int(month), 1)
    except (ValueError, AttributeError):
        raise ValidationError("Period must be in YYYY-MM format.")
    if period_start > date.today():
        raise ValidationError("Cannot compute a score for a future period.")
    month_end = date(period_start.year, period_start.month + 1, 1) if period_start.month < 12 else date(period_start.year + 1, 1, 1)
    inspections = Inspection.objects.filter(
        supplier=supplier,
        completed_at__gte=period_start,
        completed_at__lt=month_end,
    )
    completed = inspections.filter(status=Inspection.Status.COMPLETED)
    inspection_count = completed.count()
    passed = completed.filter(overall_result=Inspection.Result.PASS).count()
    pass_rate = Decimal("100.00") if inspection_count == 0 else (
        (Decimal(passed) / Decimal(inspection_count)) * Decimal("100.00")
    ).quantize(Decimal("0.01"))
    ncr_count = NonConformanceReport.objects.filter(
        supplier=supplier,
        raised_at__gte=period_start,
        raised_at__lt=month_end,
    ).count()
    capa_overdue = CorrectiveAction.objects.filter(
        owner=supplier,
        due_date__lt=date.today(),
    ).exclude(status__in=(CorrectiveAction.Status.CLOSED, CorrectiveAction.Status.CANCELLED)).count()
    score = (
        Decimal("100.00")
        - (Decimal("10.00") * (inspection_count - passed))
        + (Decimal("5.00") * ncr_count)
        - (Decimal("2.00") * capa_overdue)
    )
    score = max(score, Decimal("0.00")).quantize(Decimal("0.01"))
    quality_score, _ = SupplierQualityScore.objects.update_or_create(
        supplier=supplier,
        period=period,
        defaults={
            "score": score,
            "inspection_count": inspection_count,
            "inspection_pass_rate": pass_rate,
            "ncr_count": ncr_count,
            "capa_overdue_count": capa_overdue,
            "computed_by": actor,
            "computed_at": timezone.now(),
        },
    )
    return quality_score
