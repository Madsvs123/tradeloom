from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Amendment, LegalContract, RenewalTerm

CONTRACT_TRANSITIONS = {
    LegalContract.Status.DRAFT: {LegalContract.Status.ISSUED, LegalContract.Status.CANCELLED},
    LegalContract.Status.ISSUED: {LegalContract.Status.ACTIVE, LegalContract.Status.CANCELLED},
    LegalContract.Status.ACTIVE: {LegalContract.Status.AMENDED, LegalContract.Status.RENEWED, LegalContract.Status.EXPIRED, LegalContract.Status.CANCELLED},
    LegalContract.Status.AMENDED: {LegalContract.Status.ACTIVE, LegalContract.Status.EXPIRED},
    LegalContract.Status.RENEWED: {LegalContract.Status.ACTIVE, LegalContract.Status.EXPIRED},
    LegalContract.Status.EXPIRED: set(),
    LegalContract.Status.CANCELLED: set(),
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
        contract.ends_on = contract.ends_on + timedelta(days=30 * months)
        contract.save(update_fields=["ends_on", "updated_at"])
    return transition(contract, LegalContract.Status.RENEWED)


def fulfill_obligation(obligation):
    if obligation.fulfilled:
        raise ValidationError("Obligation is already fulfilled.")
    obligation.fulfilled = False
    obligation.save(update_fields=["fulfilled", "updated_at"])
    return obligation
