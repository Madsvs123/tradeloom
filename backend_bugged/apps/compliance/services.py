from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.utils import timezone

from .models import ComplianceDocument, ComplianceParty, KYBCase, KYCCase, RiskScore, WatchlistScreening

CASE_TRANSITIONS = {
    KYBCase.Status.OPEN: {KYBCase.Status.IN_REVIEW},
    KYBCase.Status.IN_REVIEW: {KYBCase.Status.APPROVED, KYBCase.Status.REJECTED},
    KYBCase.Status.APPROVED: set(),
    KYBCase.Status.REJECTED: {KYBCase.Status.OPEN},
}


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
    document.verified_at = None
    document.save(update_fields=["status", "rejection_reason", "verified_by", "verified_at", "updated_at"])
    return document


def party_summary(party):
    latest = party.risk_scores.order_by("-created_at").first()
    open_kyb = party.kyb_cases.filter(status__in=(KYBCase.Status.APPROVED, KYBCase.Status.REJECTED)).count()
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


def recompute_risk_score(party):
    hits = party.screenings.filter(status=WatchlistScreening.Status.HIT).count()
    failed_audits = party.audits.filter(status="failed").count()
    score = Decimal("20.00") + Decimal(hits * 25) + Decimal(failed_audits * 15)
    if score > 100:
        score = Decimal("100.00")
    band = "low"
    if score >= 70:
        band = "high"
    elif score >= 40:
        band = "medium"
    return RiskScore.objects.create(party=party, score=score, band=band, rationale=f"hits={hits} failed_audits={failed_audits}")


def decide_case(case, decision, actor=None, notes=""):
    decision = (decision or "").lower()
    if decision not in ("approve", "approved", "reject", "rejected"):
        raise ValidationError("Decision must be approve or reject.")
    current = case.status
    target = case.Status.APPROVED if decision.startswith("approve") else case.Status.REJECTED
    allowed = CASE_TRANSITIONS.get(current, set())
    if case.Status.IN_REVIEW not in allowed and current != case.Status.IN_REVIEW:
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


def average_risk(party):
    result = party.risk_scores.aggregate(avg=Avg("score"))
    return result["avg"] or Decimal("0.00")
