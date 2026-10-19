from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.utils import timezone

from .models import (
    ComplianceDocument,
    ComplianceParty,
    ComplianceTask,
    EvidenceFile,
    KYBCase,
    KYCCase,
    RiskAssessment,
    RiskScore,
    SanctionsEntry,
    ScreeningCase,
    WatchlistScreening,
)

CASE_TRANSITIONS = {
    KYBCase.Status.OPEN: {KYBCase.Status.IN_REVIEW},
    KYBCase.Status.IN_REVIEW: {KYBCase.Status.APPROVED, KYBCase.Status.REJECTED},
    KYBCase.Status.APPROVED: set(),
    KYBCase.Status.REJECTED: {KYBCase.Status.OPEN},
}

SCREENING_CASE_TRANSITIONS = {
    ScreeningCase.Status.OPEN: {ScreeningCase.Status.IN_REVIEW},
    ScreeningCase.Status.IN_REVIEW: {ScreeningCase.Status.CLEARED, ScreeningCase.Status.HIT},
    ScreeningCase.Status.CLEARED: set(),
    ScreeningCase.Status.HIT: set(),
}

COMPLIANCE_TASK_TRANSITIONS = {
    ComplianceTask.Status.OPEN: {ComplianceTask.Status.IN_PROGRESS, ComplianceTask.Status.CANCELLED},
    ComplianceTask.Status.IN_PROGRESS: {ComplianceTask.Status.COMPLETE, ComplianceTask.Status.CANCELLED},
    ComplianceTask.Status.COMPLETE: set(),
    ComplianceTask.Status.CANCELLED: set(),
}

RISK_ASSESSMENT_TRANSITIONS = {
    RiskAssessment.Status.DRAFT: {RiskAssessment.Status.SUBMITTED},
    RiskAssessment.Status.SUBMITTED: {RiskAssessment.Status.APPROVED, RiskAssessment.Status.REJECTED},
    RiskAssessment.Status.APPROVED: set(),
    RiskAssessment.Status.REJECTED: {RiskAssessment.Status.DRAFT},
}

SANCTIONS_ENTRY_TRANSITIONS = {
    SanctionsEntry.Status.ACTIVE: {SanctionsEntry.Status.MATCHED, SanctionsEntry.Status.CLEARED},
    SanctionsEntry.Status.MATCHED: set(),
    SanctionsEntry.Status.CLEARED: set(),
}


def _assert_transition(current, target, transitions):
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move from status '{current}' to '{target}'.")


def verify_document(document, reviewer, accept=True, reason=""):
    if document.status != ComplianceDocument.Status.UPLOADED:
        raise ValidationError("Only uploaded documents can be verified.")
    if accept:
        document.status = ComplianceDocument.Status.VERIFIED
        document.rejection_reason = ""
    else:
        if not reason:
            raise ValidationError("A rejection reason is required.")
        document.status = ComplianceDocument.Status.REJECTED
        document.rejection_reason = reason
    document.verified_by = reviewer
    document.verified_at = timezone.now()
    document.save(update_fields=["status", "rejection_reason", "verified_by", "verified_at", "updated_at"])
    return document


def check_document_expiry(days=30):
    cutoff = timezone.now().date() + timedelta(days=days)
    documents = ComplianceDocument.objects.filter(expires_at__lte=cutoff).order_by("expires_at")
    return [
        {
            "id": doc.pk,
            "title": doc.title,
            "document_type": doc.document_type,
            "party_id": doc.party_id,
            "party_name": doc.party.name,
            "expires_at": doc.expires_at.isoformat() if doc.expires_at else None,
            "status": doc.status,
        }
        for doc in documents
    ]


def party_summary(party):
    latest = party.risk_scores.order_by("-created_at").first()
    open_kyb = party.kyb_cases.exclude(status__in=(KYBCase.Status.APPROVED, KYBCase.Status.REJECTED)).count()
    open_kyc = party.kyc_cases.exclude(status__in=(KYCCase.Status.APPROVED, KYCCase.Status.REJECTED)).count()
    hits = party.screenings.filter(status=WatchlistScreening.Status.HIT).count()
    unverified_docs = party.documents.exclude(status=ComplianceDocument.Status.VERIFIED).count()
    return {
        "party_id": party.pk,
        "name": party.name,
        "kind": party.kind,
        "risk_score": str(latest.score) if latest else None,
        "risk_band": latest.band if latest else None,
        "open_kyb": open_kyb,
        "open_kyc": open_kyc,
        "watchlist_hits": hits,
        "unverified_documents": unverified_docs,
    }


def party_structure(party):
    owners = party.beneficial_owners.all()
    total_ownership = owners.aggregate(total=Sum("ownership_percent"))["total"] or Decimal("0.00")
    return {
        "party_id": party.pk,
        "name": party.name,
        "kind": party.kind,
        "country": party.country,
        "registration_number": party.registration_number,
        "beneficial_owners": [
            {
                "id": owner.pk,
                "full_name": owner.full_name,
                "ownership_percent": str(owner.ownership_percent),
                "nationality": owner.nationality,
                "is_controlling": owner.is_controlling,
            }
            for owner in owners
        ],
        "declared_ownership_percent": str(total_ownership),
        "due_diligence_status": (
            party.due_diligence.order_by("-created_at").first().status
            if party.due_diligence.exists()
            else None
        ),
    }


def recompute_risk_score(party):
    hits = party.screenings.filter(status=WatchlistScreening.Status.HIT).count()
    failed_audits = party.audits.filter(status="failed").count()
    score = Decimal("20.00") + Decimal(hits * 25) - Decimal(failed_audits * 15)
    if score > 100:
        score = Decimal("100.00")
    band = "low"
    if score >= 70:
        band = "high"
    elif score >= 40:
        band = "medium"
    return RiskScore.objects.create(
        party=party, score=score, band=band, rationale=f"hits={hits} failed_audits={failed_audits}"
    )


def decide_case(case, decision, actor=None, notes=""):
    decision = (decision or "").lower()
    if decision not in ("approve", "approved", "reject", "rejected"):
        raise ValidationError("Decision must be approve or reject.")
    current = case.status
    target = case.Status.APPROVED if decision.startswith("approve") else case.Status.REJECTED
    allowed = CASE_TRANSITIONS.get(current, set())
    if current == case.Status.OPEN:
        case.status = case.Status.IN_REVIEW
        case.save(update_fields=["status", "updated_at"])
        current = case.status
        allowed = CASE_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot decide a case in status '{current}'.")
    case.status = target
    case.assigned_to = actor
    case.notes = notes or case.notes
    case.decided_at = timezone.now()
    case.save(update_fields=["status", "assigned_to", "notes", "decided_at", "updated_at"])
    return case


def start_screening_review(case, actor=None):
    _assert_transition(case.status, ScreeningCase.Status.IN_REVIEW, SCREENING_CASE_TRANSITIONS)
    case.status = ScreeningCase.Status.IN_REVIEW
    case.assigned_to = actor
    case.save(update_fields=["status", "assigned_to", "updated_at"])
    return case


def decide_screening_case(case, decision, actor=None, notes=""):
    decision = (decision or "").lower()
    if decision not in ("clear", "cleared", "hit"):
        raise ValidationError("Decision must be clear or hit.")
    target = ScreeningCase.Status.CLEARED if decision.startswith("clear") else ScreeningCase.Status.HIT
    _assert_transition(case.status, target, SCREENING_CASE_TRANSITIONS)
    case.status = target
    case.decided_by = actor
    case.decided_at = timezone.now()
    case.notes = notes or case.notes
    case.save(update_fields=["status", "decided_by", "decided_at", "notes", "updated_at"])
    if target == ScreeningCase.Status.HIT:
        WatchlistScreening.objects.create(
            party=case.party,
            list_name=case.list_name,
            status=WatchlistScreening.Status.HIT,
            matches=case.matched_records or [{"case_id": case.pk, "list_name": case.list_name}],
        )
    return case


def start_task(task, actor=None):
    _assert_transition(task.status, ComplianceTask.Status.IN_PROGRESS, COMPLIANCE_TASK_TRANSITIONS)
    task.status = ComplianceTask.Status.IN_PROGRESS
    task.assignee = actor or task.assignee
    task.save(update_fields=["status", "assignee", "updated_at"])
    return task


def complete_task(task):
    _assert_transition(task.status, ComplianceTask.Status.COMPLETE, COMPLIANCE_TASK_TRANSITIONS)
    task.status = ComplianceTask.Status.COMPLETE
    task.completed_at = timezone.now()
    task.save(update_fields=["status", "completed_at", "updated_at"])
    return task


def cancel_task(task):
    _assert_transition(task.status, ComplianceTask.Status.CANCELLED, COMPLIANCE_TASK_TRANSITIONS)
    task.status = ComplianceTask.Status.CANCELLED
    task.save(update_fields=["status", "updated_at"])
    return task


def submit_risk_assessment(assessment):
    _assert_transition(assessment.status, RiskAssessment.Status.SUBMITTED, RISK_ASSESSMENT_TRANSITIONS)
    if assessment.overall_score < 0 or assessment.overall_score > 100:
        raise ValidationError("Overall score must be between 0 and 100.")
    if assessment.overall_score >= 70:
        assessment.band = "high"
    elif assessment.overall_score >= 40:
        assessment.band = "medium"
    else:
        assessment.band = "low"
    assessment.status = RiskAssessment.Status.SUBMITTED
    assessment.save(update_fields=["status", "band", "updated_at"])
    return assessment


def approve_risk_assessment(assessment, actor=None):
    _assert_transition(assessment.status, RiskAssessment.Status.APPROVED, RISK_ASSESSMENT_TRANSITIONS)
    assessment.status = RiskAssessment.Status.APPROVED
    assessment.decided_by = actor
    assessment.decided_at = timezone.now()
    assessment.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
    RiskScore.objects.create(
        party=assessment.party, score=assessment.overall_score, band=assessment.band, rationale=assessment.recommendations
    )
    return assessment


def reject_risk_assessment(assessment, actor=None, reason=""):
    _assert_transition(assessment.status, RiskAssessment.Status.REJECTED, RISK_ASSESSMENT_TRANSITIONS)
    if not reason:
        raise ValidationError("A rejection reason is required.")
    assessment.status = RiskAssessment.Status.REJECTED
    assessment.decided_by = actor
    assessment.decided_at = timezone.now()
    assessment.recommendations = (assessment.recommendations + "\n" if assessment.recommendations else "") + (
        f"Rejected: {reason}"
    )
    assessment.save(update_fields=["status", "decided_by", "decided_at", "recommendations", "updated_at"])
    return assessment


def decide_sanctions_entry(entry, decision, case=None):
    decision = (decision or "").lower()
    if decision not in ("match", "matched", "clear", "cleared"):
        raise ValidationError("Decision must be match or clear.")
    target = SanctionsEntry.Status.MATCHED if decision.startswith("match") else SanctionsEntry.Status.CLEARED
    _assert_transition(entry.status, target, SANCTIONS_ENTRY_TRANSITIONS)
    entry.status = target
    entry.matched_case = case
    entry.save(update_fields=["status", "matched_case", "updated_at"])
    return entry


def create_evidence_file(party, title, file_url, uploaded_by, case_type="", case_id="", description=""):
    if not title or not file_url:
        raise ValidationError("Title and file URL are required.")
    return EvidenceFile.objects.create(
        party=party,
        title=title,
        file_url=file_url,
        uploaded_by=uploaded_by,
        case_type=case_type,
        case_id=case_id,
        description=description,
    )


def average_risk(party):
    result = party.risk_scores.aggregate(avg=Avg("score"))
    return result["avg"] or Decimal("0.00")
