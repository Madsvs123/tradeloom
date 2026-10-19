from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    BankGuarantee,
    CreditInsurancePolicy,
    FactoringAgreement,
    FinanceDisbursement,
    FinancingOffer,
    InvoiceFinancingRequest,
    LcAmendment,
    LetterOfCredit,
    RepaymentSchedule,
)

LC_TRANSITIONS = {
    LetterOfCredit.Status.DRAFT: {LetterOfCredit.Status.ISSUED, LetterOfCredit.Status.CANCELLED},
    LetterOfCredit.Status.ISSUED: {
        LetterOfCredit.Status.AMENDED,
        LetterOfCredit.Status.CONFIRMED,
        LetterOfCredit.Status.NEGOTIATED,
        LetterOfCredit.Status.MATURED,
        LetterOfCredit.Status.CLOSED,
    },
    LetterOfCredit.Status.AMENDED: {
        LetterOfCredit.Status.CONFIRMED,
        LetterOfCredit.Status.NEGOTIATED,
        LetterOfCredit.Status.MATURED,
        LetterOfCredit.Status.CLOSED,
    },
    LetterOfCredit.Status.CONFIRMED: {
        LetterOfCredit.Status.NEGOTIATED,
        LetterOfCredit.Status.MATURED,
        LetterOfCredit.Status.CLOSED,
    },
    LetterOfCredit.Status.NEGOTIATED: {LetterOfCredit.Status.MATURED, LetterOfCredit.Status.CLOSED},
    LetterOfCredit.Status.MATURED: {LetterOfCredit.Status.CLOSED},
    LetterOfCredit.Status.CLOSED: set(),
    LetterOfCredit.Status.CANCELLED: set(),
}

REQUEST_TRANSITIONS = {
    InvoiceFinancingRequest.Status.DRAFT: {
        InvoiceFinancingRequest.Status.SUBMITTED,
        InvoiceFinancingRequest.Status.CANCELLED,
    },
    InvoiceFinancingRequest.Status.SUBMITTED: {
        InvoiceFinancingRequest.Status.UNDER_REVIEW,
        InvoiceFinancingRequest.Status.REJECTED,
        InvoiceFinancingRequest.Status.CANCELLED,
    },
    InvoiceFinancingRequest.Status.UNDER_REVIEW: {
        InvoiceFinancingRequest.Status.OFFERED,
        InvoiceFinancingRequest.Status.REJECTED,
        InvoiceFinancingRequest.Status.CANCELLED,
    },
    InvoiceFinancingRequest.Status.OFFERED: {
        InvoiceFinancingRequest.Status.ACCEPTED,
        InvoiceFinancingRequest.Status.CANCELLED,
    },
    InvoiceFinancingRequest.Status.ACCEPTED: {InvoiceFinancingRequest.Status.FUNDED},
    InvoiceFinancingRequest.Status.FUNDED: {InvoiceFinancingRequest.Status.REPAID},
    InvoiceFinancingRequest.Status.REPAID: set(),
    InvoiceFinancingRequest.Status.REJECTED: set(),
    InvoiceFinancingRequest.Status.CANCELLED: set(),
}

OFFER_TRANSITIONS = {
    FinancingOffer.Status.DRAFT: {FinancingOffer.Status.ISSUED, FinancingOffer.Status.EXPIRED},
    FinancingOffer.Status.ISSUED: {FinancingOffer.Status.ACCEPTED, FinancingOffer.Status.DECLINED, FinancingOffer.Status.EXPIRED},
    FinancingOffer.Status.ACCEPTED: set(),
    FinancingOffer.Status.DECLINED: set(),
    FinancingOffer.Status.EXPIRED: set(),
}

GUARANTEE_TRANSITIONS = {
    BankGuarantee.Status.DRAFT: {BankGuarantee.Status.ISSUED, BankGuarantee.Status.CANCELLED},
    BankGuarantee.Status.ISSUED: {
        BankGuarantee.Status.CLAIMED,
        BankGuarantee.Status.RELEASED,
        BankGuarantee.Status.EXPIRED,
    },
    BankGuarantee.Status.CLAIMED: {BankGuarantee.Status.RELEASED},
    BankGuarantee.Status.RELEASED: set(),
    BankGuarantee.Status.EXPIRED: set(),
    BankGuarantee.Status.CANCELLED: set(),
}

POLICY_TRANSITIONS = {
    CreditInsurancePolicy.Status.DRAFT: {CreditInsurancePolicy.Status.ACTIVE, CreditInsurancePolicy.Status.CANCELLED},
    CreditInsurancePolicy.Status.ACTIVE: {CreditInsurancePolicy.Status.EXPIRED, CreditInsurancePolicy.Status.CANCELLED},
    CreditInsurancePolicy.Status.EXPIRED: set(),
    CreditInsurancePolicy.Status.CANCELLED: set(),
}


def record_request_status(request_obj, to_status, actor=None, note=""):
    allowed = REQUEST_TRANSITIONS.get(request_obj.status, set())
    if to_status not in allowed:
        raise ValidationError(
            f"Cannot move financing request from '{request_obj.status}' to '{to_status}'."
        )
    request_obj.status = to_status
    if note:
        request_obj.notes = f"{request_obj.notes}\n{note}".strip()
    request_obj.save(update_fields=["status", "notes", "updated_at"])
    return request_obj


def issue_lc(lc, actor=None):
    allowed = LC_TRANSITIONS.get(lc.status, set())
    if LetterOfCredit.Status.ISSUED not in allowed:
        raise ValidationError("Only draft letters of credit can be issued.")
    if lc.applicant_id == lc.beneficiary_id:
        raise ValidationError("The applicant and beneficiary must be different parties.")
    if lc.amount <= 0:
        raise ValidationError("The LC amount must be positive.")
    if lc.expiry_date <= timezone.localdate():
        raise ValidationError("The LC expiry date must be in the future.")
    if not lc.issuing_bank:
        raise ValidationError("An issuing bank is required.")
    lc.status = LetterOfCredit.Status.ISSUED
    lc.issued_at = timezone.now()
    lc.save(update_fields=["status", "issued_at", "updated_at"])
    return lc


@transaction.atomic
def request_lc_amendment(lc, requested_by, amendment_type, description="", new_amount=None, new_expiry_date=None):
    if lc.status not in (LetterOfCredit.Status.ISSUED, LetterOfCredit.Status.AMENDED):
        raise ValidationError("Amendments can only be requested against issued LCs.")
    if new_amount is None and new_expiry_date is None:
        raise ValidationError("An amendment must change the amount or the expiry date.")
    return LcAmendment.objects.create(
        lc=lc,
        requested_by=requested_by,
        amendment_type=amendment_type,
        description=description,
        new_amount=new_amount,
        new_expiry_date=new_expiry_date,
    )


def approve_lc_amendment(amendment, actor):
    if amendment.status != LcAmendment.Status.REQUESTED:
        raise ValidationError("Only requested amendments can be approved.")
    amendment.status = LcAmendment.Status.APPROVED
    amendment.approved_by = actor
    amendment.approved_at = timezone.now()
    amendment.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
    return amendment


def reject_lc_amendment(amendment, actor=None):
    if amendment.status != LcAmendment.Status.REQUESTED:
        raise ValidationError("Only requested amendments can be rejected.")
    amendment.status = LcAmendment.Status.REJECTED
    amendment.save(update_fields=["status", "updated_at"])
    return amendment


@transaction.atomic
def apply_lc_amendment(amendment, actor=None):
    if amendment.status != LcAmendment.Status.APPROVED:
        raise ValidationError("Only approved amendments can be applied.")
    lc = amendment.lc
    if amendment.new_amount is not None:
        lc.amount = amendment.new_amount
    if amendment.new_expiry_date is not None:
        lc.expiry_date = amendment.new_expiry_date
    if lc.status != LetterOfCredit.Status.AMENDED:
        lc.status = LetterOfCredit.Status.AMENDED
    amendment.status = LcAmendment.Status.APPLIED
    amendment.applied_at = timezone.now()
    lc.save(update_fields=["amount", "expiry_date", "status", "updated_at"])
    amendment.save(update_fields=["status", "applied_at", "updated_at"])
    return amendment


def issue_guarantee(guarantee, actor=None):
    allowed = GUARANTEE_TRANSITIONS.get(guarantee.status, set())
    if BankGuarantee.Status.ISSUED not in allowed:
        raise ValidationError("Only draft guarantees can be issued.")
    if guarantee.amount <= 0:
        raise ValidationError("The guarantee amount must be positive.")
    if guarantee.expiry_date and guarantee.expiry_date <= timezone.localdate():
        raise ValidationError("The guarantee expiry date must be in the future.")
    guarantee.status = BankGuarantee.Status.ISSUED
    guarantee.issue_date = timezone.localdate()
    guarantee.save(update_fields=["status", "issue_date", "updated_at"])
    return guarantee


def activate_policy(policy, actor=None):
    allowed = POLICY_TRANSITIONS.get(policy.status, set())
    if CreditInsurancePolicy.Status.ACTIVE not in allowed:
        raise ValidationError("Only draft policies can be activated.")
    policy.status = CreditInsurancePolicy.Status.ACTIVE
    policy.save(update_fields=["status", "updated_at"])
    return policy


def submit_financing_request(request_obj, actor=None):
    if request_obj.status != InvoiceFinancingRequest.Status.DRAFT:
        raise ValidationError(f"Cannot submit a request in status '{request_obj.status}'.")
    if request_obj.requested_amount >= request_obj.invoice_amount:
        raise ValidationError("The requested amount cannot exceed the invoice amount.")
    if request_obj.requested_amount <= 0:
        raise ValidationError("The requested amount must be positive.")
    request_obj.status = InvoiceFinancingRequest.Status.SUBMITTED
    request_obj.submitted_at = timezone.now()
    request_obj.save(update_fields=["status", "submitted_at", "updated_at"])
    return request_obj


def review_financing_request(request_obj, actor=None, approved=True):
    if request_obj.status != InvoiceFinancingRequest.Status.SUBMITTED:
        raise ValidationError("Only submitted requests can be reviewed.")
    return record_request_status(
        request_obj,
        InvoiceFinancingRequest.Status.UNDER_REVIEW if approved else InvoiceFinancingRequest.Status.REJECTED,
        actor=actor,
    )


@transaction.atomic
def make_offer(request_obj, offered_by, amount, rate, tenor_days=30, fees=0, valid_until=None):
    if request_obj.status not in (
        InvoiceFinancingRequest.Status.SUBMITTED,
        InvoiceFinancingRequest.Status.UNDER_REVIEW,
        InvoiceFinancingRequest.Status.OFFERED,
    ):
        raise ValidationError("Offers can only be made against reviewable requests.")
    if amount is None or rate is None:
        raise ValidationError("Offer amount and rate are required.")
    amount = Decimal(str(amount))
    if amount <= 0 or amount > request_obj.requested_amount:
        raise ValidationError(f"Offer amount must be between 0 and {request_obj.requested_amount}.")
    offer = FinancingOffer.objects.create(
        request=request_obj,
        offered_by=offered_by,
        status=FinancingOffer.Status.ISSUED,
        amount=amount,
        currency=request_obj.currency,
        rate=Decimal(str(rate)),
        tenor_days=tenor_days,
        fees=Decimal(str(fees)),
        valid_until=valid_until,
        issued_at=timezone.now(),
    )
    record_request_status(request_obj, InvoiceFinancingRequest.Status.OFFERED, actor=offered_by)
    return offer


@transaction.atomic
def accept_offer(offer, actor=None):
    allowed = OFFER_TRANSITIONS.get(offer.status, set())
    if FinancingOffer.Status.ACCEPTED not in allowed:
        raise ValidationError("Only issued offers can be accepted.")
    if offer.valid_until and offer.valid_until < timezone.now():
        offer.status = FinancingOffer.Status.EXPIRED
        offer.save(update_fields=["status", "updated_at"])
        raise ValidationError("This offer has expired.")
    offer.status = FinancingOffer.Status.ACCEPTED
    offer.accepted_at = timezone.now()
    offer.save(update_fields=["status", "accepted_at", "updated_at"])
    request_obj = offer.request
    record_request_status(request_obj, InvoiceFinancingRequest.Status.ACCEPTED, actor=actor)
    FinanceDisbursement.objects.create(
        request=request_obj,
        recipient=request_obj.applicant,
        amount=offer.amount,
        currency=offer.currency,
    )
    interest = (offer.amount * offer.rate / Decimal("100.00") * offer.tenor_days / Decimal("365.00")).quantize(
        Decimal("0.01")
    )
    RepaymentSchedule.objects.create(
        request=request_obj,
        due_date=timezone.localdate() + timedelta(days=offer.tenor_days),
        principal=request_obj.requested_amount,
        interest=interest,
        total_due=(offer.amount + interest).quantize(Decimal("0.01")),
    )
    return offer


def decline_offer(offer, actor=None):
    allowed = OFFER_TRANSITIONS.get(offer.status, set())
    if FinancingOffer.Status.DECLINED not in allowed:
        raise ValidationError("Only issued offers can be declined.")
    offer.status = FinancingOffer.Status.DECLINED
    offer.save(update_fields=["status", "updated_at"])
    return offer


@transaction.atomic
def fund_disbursement(disbursement, actor=None):
    if disbursement.status != FinanceDisbursement.Status.REQUESTED:
        raise ValidationError("Only requested disbursements can be funded.")
    disbursement.status = FinanceDisbursement.Status.DISBURSED
    disbursement.disbursed_at = timezone.now()
    disbursement.save(update_fields=["status", "disbursed_at", "updated_at"])
    request_obj = disbursement.request
    if request_obj and request_obj.status == InvoiceFinancingRequest.Status.ACCEPTED:
        request_obj.status = InvoiceFinancingRequest.Status.FUNDED
        request_obj.funded_at = timezone.now()
        request_obj.save(update_fields=["status", "funded_at", "updated_at"])
    return disbursement


def fail_disbursement(disbursement, reason, actor=None):
    if disbursement.status != FinanceDisbursement.Status.REQUESTED:
        raise ValidationError("Only requested disbursements can be marked as failed.")
    disbursement.status = FinanceDisbursement.Status.FAILED
    disbursement.failure_reason = reason
    disbursement.save(update_fields=["status", "failure_reason", "updated_at"])
    return disbursement


@transaction.atomic
def record_repayment(schedule, actor, amount):
    if schedule.status == RepaymentSchedule.Status.PAID:
        raise ValidationError("This repayment schedule has already been paid.")
    if amount is None:
        raise ValidationError("Repayment amount is required.")
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Repayment amount must be positive.")
    schedule.paid_amount = amount
    schedule.status = (
        RepaymentSchedule.Status.PAID if amount >= schedule.total_due else RepaymentSchedule.Status.LATE
    )
    schedule.paid_at = timezone.now()
    schedule.paid_by = actor
    schedule.save(update_fields=["paid_amount", "status", "paid_at", "paid_by", "updated_at"])
    request_obj = schedule.request
    if request_obj.status == InvoiceFinancingRequest.Status.FUNDED:
        unpaid = request_obj.repayment_schedules.exclude(status=RepaymentSchedule.Status.PAID)
        if not unpaid.exists():
            request_obj.status = InvoiceFinancingRequest.Status.REPAID
            request_obj.repaid_at = timezone.now()
            request_obj.save(update_fields=["status", "repaid_at", "updated_at"])
    return schedule


def activate_factoring_agreement(agreement, actor=None):
    if agreement.status != FactoringAgreement.Status.DRAFT:
        raise ValidationError("Only draft factoring agreements can be activated.")
    agreement.status = FactoringAgreement.Status.ACTIVE
    agreement.signed_at = timezone.now()
    agreement.save(update_fields=["status", "signed_at", "updated_at"])
    return agreement
