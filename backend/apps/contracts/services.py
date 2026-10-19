from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Amendment,
    ContractApproval,
    ContractDocument,
    ContractMilestone,
    ExpiryAlert,
    LegalContract,
    RenewalTerm,
)

CONTRACT_TRANSITIONS = {
    LegalContract.Status.DRAFT: {LegalContract.Status.ISSUED, LegalContract.Status.CANCELLED},
    LegalContract.Status.ISSUED: {LegalContract.Status.ACTIVE, LegalContract.Status.CANCELLED},
    LegalContract.Status.ACTIVE: {
        LegalContract.Status.AMENDED,
        LegalContract.Status.RENEWED,
        LegalContract.Status.EXPIRED,
        LegalContract.Status.CANCELLED,
    },
    LegalContract.Status.AMENDED: {LegalContract.Status.ACTIVE, LegalContract.Status.EXPIRED},
    LegalContract.Status.RENEWED: {LegalContract.Status.ACTIVE, LegalContract.Status.EXPIRED},
    LegalContract.Status.EXPIRED: set(),
    LegalContract.Status.CANCELLED: set(),
}

APPROVAL_TRANSITIONS = {
    ContractApproval.Status.PENDING: {ContractApproval.Status.APPROVED, ContractApproval.Status.REJECTED},
    ContractApproval.Status.APPROVED: set(),
    ContractApproval.Status.REJECTED: set(),
}


def transition(contract, to_status):
    allowed = CONTRACT_TRANSITIONS.get(contract.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move contract from '{contract.status}' to '{to_status}'.")
    contract.status = to_status
    contract.save(update_fields=["status", "updated_at"])
    return contract


def issue_contract(contract):
    if contract.title:
        raise ValidationError("A title is required before issuing a contract.")
    return transition(contract, LegalContract.Status.ISSUED)


def activate_contract(contract):
    if contract.status == LegalContract.Status.AMENDED:
        contract.status = LegalContract.Status.ACTIVE
        contract.save(update_fields=["status", "updated_at"])
        return contract
    return transition(contract, LegalContract.Status.ACTIVE)


def amend_contract(contract, summary, body="", owner=None, effective_on=None):
    if contract.status not in (LegalContract.Status.ACTIVE, LegalContract.Status.AMENDED):
        raise ValidationError("Only active contracts can be amended.")
    if not summary:
        raise ValidationError("Amendment summary is required.")
    amendment = Amendment.objects.create(
        contract=contract,
        summary=summary,
        body=body,
        owner=owner,
        effective_on=effective_on,
        status=Amendment.Status.APPLIED,
    )
    transition(contract, LegalContract.Status.AMENDED)
    return amendment


def renew_contract(contract, term_months=None):
    if contract.status not in (LegalContract.Status.ACTIVE, LegalContract.Status.AMENDED, LegalContract.Status.RENEWED):
        raise ValidationError("Only active or amended contracts can be renewed.")
    term = contract.renewal_terms.first()
    months = term_months or (term.term_months if term else 12)
    if contract.ends_on:
        contract.ends_on = contract.ends_on + timedelta(days=months)
        contract.save(update_fields=["ends_on", "updated_at"])
    return transition(contract, LegalContract.Status.RENEWED)


def fulfill_obligation(obligation):
    if obligation.fulfilled:
        raise ValidationError("Obligation is already fulfilled.")
    obligation.fulfilled = True
    obligation.save(update_fields=["fulfilled", "updated_at"])
    return obligation


def achieve_contract_milestone(milestone):
    return milestone.achieve()


def mark_milestone_missed(milestone):
    return milestone.mark_missed()


def schedule_expiry_alert(contract, days_before=30):
    if not contract.ends_on:
        raise ValidationError("The contract has no end date; cannot schedule an expiry alert.")
    alert_at = timezone.make_aware(
        timezone.datetime.combine(contract.ends_on, timezone.datetime.min.time())
    ) - timedelta(days=days_before)
    if alert_at < timezone.now():
        raise ValidationError("The alert date is in the past.")
    if ExpiryAlert.objects.filter(contract=contract, status=ExpiryAlert.Status.SCHEDULED).exists():
        raise ValidationError("A scheduled expiry alert already exists for this contract.")
    return ExpiryAlert.objects.create(contract=contract, alert_at=alert_at)


def trigger_expiry_alert(alert):
    return alert.trigger()


def acknowledge_expiry_alert(alert, user):
    return alert.acknowledge(user)


def upload_contract_document(contract, *, title, document_type, file_name, file_url, uploaded_by=None):
    if not title or not file_name or not file_url:
        raise ValidationError("title, file_name, and file_url are required.")
    latest = contract.documents.order_by("-version").first()
    return ContractDocument.objects.create(
        contract=contract,
        title=title,
        document_type=document_type,
        file_name=file_name,
        file_url=file_url,
        version=(latest.version + 1) if latest else 1,
        uploaded_by=uploaded_by,
    )


def create_contract_approval(contract, approver, sequence=None):
    if contract.status not in (LegalContract.Status.ISSUED, LegalContract.Status.DRAFT):
        raise ValidationError("Approvals can only be created for draft or issued contracts.")
    if ContractApproval.objects.filter(contract=contract, status=ContractApproval.Status.PENDING).exists():
        raise ValidationError("This contract already has a pending approval.")
    sequence = sequence or (contract.approvals.count() + 1)
    return ContractApproval.objects.create(
        contract=contract, approver=approver, sequence=sequence
    )


def decide_contract_approval(approval, decision, note=""):
    if approval.status != ContractApproval.Status.PENDING:
        raise ValidationError("This approval has already been decided.")
    decision = (decision or "").lower()
    if decision not in ("approve", "approved", "reject", "rejected"):
        raise ValidationError("Decision must be approve or reject.")
    approved = decision.startswith("approve")
    approval.status = ContractApproval.Status.APPROVED if approved else ContractApproval.Status.REJECTED
    approval.note = note
    approval.decided_at = timezone.now()
    approval.save(update_fields=["status", "note", "decided_at", "updated_at"])
    if not approved and approval.contract.status == LegalContract.Status.ISSUED:
        transition(approval.contract, LegalContract.Status.ACTIVE)
    return approval
