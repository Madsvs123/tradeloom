import uuid

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    BankAccount,
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    FinanceApproval,
    FinanceStatement,
    InvoiceMatch,
    LedgerEntry,
    PaymentRun,
    PayoutInstruction,
    ReconciliationBatch,
    SettlementBatch,
    TaxAssessment,
    Wallet,
)

Q = Decimal("0.01")

PAYMENT_RUN_TRANSITIONS = {
    PaymentRun.Status.DRAFT: {PaymentRun.Status.SCHEDULED, PaymentRun.Status.CANCELLED},
    PaymentRun.Status.SCHEDULED: {PaymentRun.Status.EXECUTING, PaymentRun.Status.CANCELLED},
    PaymentRun.Status.EXECUTING: {PaymentRun.Status.COMPLETED, PaymentRun.Status.FAILED},
    PaymentRun.Status.COMPLETED: set(),
    PaymentRun.Status.FAILED: set(),
    PaymentRun.Status.CANCELLED: set(),
}

INVOICE_MATCH_TRANSITIONS = {
    InvoiceMatch.Status.PENDING: {InvoiceMatch.Status.MATCHED, InvoiceMatch.Status.PARTIAL, InvoiceMatch.Status.REJECTED},
    InvoiceMatch.Status.PARTIAL: {InvoiceMatch.Status.MATCHED, InvoiceMatch.Status.REJECTED},
    InvoiceMatch.Status.MATCHED: set(),
    InvoiceMatch.Status.REJECTED: set(),
}

APPROVAL_TRANSITIONS = {
    FinanceApproval.Status.PENDING: {FinanceApproval.Status.APPROVED, FinanceApproval.Status.REJECTED},
    FinanceApproval.Status.APPROVED: set(),
    FinanceApproval.Status.REJECTED: set(),
}


def _ref(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def money(value):
    return Decimal(value or 0).quantize(Q)


def _assert_transition(current, target, transitions):
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move from status '{current}' to '{target}'.")


def wallet_summary(wallet):
    return {
        "id": wallet.pk,
        "kind": wallet.kind,
        "currency": wallet.currency,
        "available": str(wallet.available),
        "held": str(wallet.held),
        "total": str(wallet.total),
        "is_active": wallet.is_active,
    }


def wallet_balances(user):
    wallets = Wallet.objects.filter(owner=user)
    balances = []
    for currency in wallets.values_list("currency", flat=True).distinct():
        currency_wallets = wallets.filter(currency=currency)
        totals = currency_wallets.aggregate(
            available=Sum("available"), held=Sum("held")
        )
        balances.append(
            {
                "currency": currency,
                "available": str(totals["available"] or Decimal("0.00")),
                "held": str(totals["held"] or Decimal("0.00")),
                "total": str((totals["available"] or Decimal("0.00")) + (totals["held"] or Decimal("0.00"))),
                "wallet_count": currency_wallets.count(),
            }
        )
    return {"user_id": user.pk, "balances": balances}


def post_ledger_entry(entry, actor=None):
    if entry.status != LedgerEntry.Status.DRAFT:
        raise ValidationError("Only draft ledger entries can be posted.")
    if entry.amount <= 0:
        raise ValidationError("Ledger amount must be positive.")
    if entry.debit_account_id == entry.credit_account_id:
        raise ValidationError("Debit and credit accounts must differ.")
    entry.status = LedgerEntry.Status.POSTED
    entry.posted_at = timezone.now()
    entry.posted_by = actor
    if not entry.reference:
        entry.reference = _ref("LE")
    entry.save(update_fields=["status", "posted_at", "posted_by", "reference", "updated_at"])
    return entry


@transaction.atomic
def fund_escrow(escrow, amount=None):
    if escrow.status not in (EscrowAccount.Status.OPEN,):
        raise ValidationError(f"Cannot fund escrow in status '{escrow.status}'.")
    amount = money(escrow.amount if amount is None else amount)
    if amount <= 0:
        raise ValidationError("Escrow fund amount must be positive.")
    buyer = escrow.buyer_wallet
    if buyer.available < amount:
        raise ValidationError("Buyer wallet has insufficient available funds.")
    buyer.available = money(buyer.available - amount)
    buyer.held = money(buyer.held + amount)
    buyer.save(update_fields=["available", "held", "updated_at"])
    escrow.amount = amount
    escrow.status = EscrowAccount.Status.FUNDED
    escrow.save(update_fields=["amount", "status", "updated_at"])
    EscrowHold.objects.create(escrow=escrow, amount=amount, currency=escrow.currency)
    return escrow


@transaction.atomic
def release_escrow(escrow):
    if escrow.status != EscrowAccount.Status.FUNDED:
        raise ValidationError("Only funded escrow can be released.")
    hold = escrow.holds.filter(status=EscrowHold.Status.HELD).first()
    if hold is None:
        raise ValidationError("No active escrow hold to release.")
    buyer = escrow.buyer_wallet
    seller = escrow.seller_wallet
    buyer.held = money(buyer.held - hold.amount)
    seller.available = money(seller.available + hold.amount)
    buyer.save(update_fields=["held", "updated_at"])
    seller.save(update_fields=["available", "updated_at"])
    hold.status = EscrowHold.Status.RELEASED
    hold.save(update_fields=["status", "updated_at"])
    escrow.status = EscrowAccount.Status.RELEASED
    escrow.save(update_fields=["status", "updated_at"])
    return escrow


@transaction.atomic
def refund_escrow(escrow):
    if escrow.status != EscrowAccount.Status.FUNDED:
        raise ValidationError("Only funded escrow can be refunded.")
    hold = escrow.holds.filter(status=EscrowHold.Status.HELD).first()
    if hold is None:
        raise ValidationError("No active escrow hold to refund.")
    buyer = escrow.buyer_wallet
    buyer.held = money(buyer.held - hold.amount)
    buyer.available = money(buyer.available + hold.amount)
    buyer.save(update_fields=["held", "available", "updated_at"])
    hold.status = EscrowHold.Status.REFUNDED
    hold.save(update_fields=["status", "updated_at"])
    escrow.status = EscrowAccount.Status.REFUNDED
    escrow.save(update_fields=["status", "updated_at"])
    return escrow


def settle_batch(batch):
    if batch.status != SettlementBatch.Status.OPEN:
        raise ValidationError("Only open settlement batches can be settled.")
    batch.net_amount = money(batch.gross_amount + batch.fee_amount)
    batch.status = SettlementBatch.Status.SETTLED
    batch.settled_at = timezone.now()
    batch.save(update_fields=["net_amount", "status", "settled_at", "updated_at"])
    return batch


def approve_payout(payout, actor=None):
    if payout.status != PayoutInstruction.Status.DRAFT:
        raise ValidationError("Only draft payouts can be approved.")
    payout.status = PayoutInstruction.Status.APPROVED
    payout.save(update_fields=["status", "updated_at"])
    return payout


@transaction.atomic
def send_payout(payout):
    if payout.status != PayoutInstruction.Status.APPROVED:
        raise ValidationError("Only approved payouts can be sent.")
    wallet = payout.wallet
    if wallet.available < payout.amount:
        raise ValidationError("Wallet has insufficient available funds for payout.")
    wallet.available = money(wallet.available - payout.amount)
    wallet.save(update_fields=["available", "updated_at"])
    payout.status = PayoutInstruction.Status.SENT
    payout.sent_at = timezone.now()
    payout.save(update_fields=["status", "sent_at", "updated_at"])
    return payout


def verify_bank_account(account, actor=None):
    if account.verified:
        raise ValidationError("Bank account is already verified.")
    if not account.account_number or not account.bank_name:
        raise ValidationError("Bank account details are incomplete.")
    account.verified = True
    account.verified_at = timezone.now()
    account.verified_by = actor
    account.save(update_fields=["verified", "verified_at", "verified_by", "updated_at"])
    return account


def deactivate_bank_account(account):
    if not account.is_active:
        raise ValidationError("Bank account is already inactive.")
    account.is_active = False
    account.save(update_fields=["is_active", "updated_at"])
    return account


def schedule_payment_run(payment_run):
    _assert_transition(payment_run.status, PaymentRun.Status.SCHEDULED, PAYMENT_RUN_TRANSITIONS)
    if not payment_run.payouts.exists():
        raise ValidationError("A payment run must contain at least one payout.")
    if payment_run.payouts.filter(status=PayoutInstruction.Status.DRAFT).exists():
        raise ValidationError("All payouts must be approved before scheduling a payment run.")
    payment_run.status = PaymentRun.Status.SCHEDULED
    payment_run.scheduled_at = timezone.now()
    payment_run.save(update_fields=["status", "scheduled_at", "updated_at"])
    return payment_run


@transaction.atomic
def execute_payment_run(payment_run, actor=None):
    _assert_transition(payment_run.status, PaymentRun.Status.EXECUTING, PAYMENT_RUN_TRANSITIONS)
    payouts = list(payment_run.payouts.all())
    if not payouts:
        raise ValidationError("A payment run must contain at least one payout.")
    for payout in payouts:
        if payout.status != PayoutInstruction.Status.APPROVED:
            raise ValidationError(f"Payout {payout.pk} is not approved; cannot execute the run.")
        if payout.wallet.available < payout.amount:
            raise ValidationError(
                f"Wallet for payout {payout.pk} has insufficient available funds."
            )
    payment_run.status = PaymentRun.Status.EXECUTING
    payment_run.save(update_fields=["status", "updated_at"])
    total = Decimal("0.00")
    for payout in payouts:
        wallet = payout.wallet
        wallet.available = money(wallet.available - payout.amount)
        wallet.save(update_fields=["available", "updated_at"])
        payout.status = PayoutInstruction.Status.SENT
        payout.sent_at = timezone.now()
        payout.save(update_fields=["status", "sent_at", "updated_at"])
        total = money(total + payout.amount)
    payment_run.total_amount = total
    payment_run.status = PaymentRun.Status.COMPLETED
    payment_run.executed_at = timezone.now()
    payment_run.executed_by = actor
    payment_run.save(update_fields=["total_amount", "status", "executed_at", "executed_by", "updated_at"])
    return payment_run


def cancel_payment_run(payment_run):
    _assert_transition(payment_run.status, PaymentRun.Status.CANCELLED, PAYMENT_RUN_TRANSITIONS)
    payment_run.status = PaymentRun.Status.CANCELLED
    payment_run.save(update_fields=["status", "updated_at"])
    return payment_run


@transaction.atomic
def match_invoice(invoice_match, actor=None):
    _assert_transition(invoice_match.status, InvoiceMatch.Status.MATCHED, INVOICE_MATCH_TRANSITIONS)
    if invoice_match.actual_amount <= 0:
        raise ValidationError("Actual amount must be positive to match an invoice.")
    invoice_match.variance = money(invoice_match.expected_amount - invoice_match.actual_amount)
    invoice_match.status = (
        InvoiceMatch.Status.PARTIAL if invoice_match.variance == 0 else InvoiceMatch.Status.MATCHED
    )
    invoice_match.matched_at = timezone.now()
    invoice_match.matched_by = actor
    invoice_match.rejection_reason = ""
    invoice_match.save(
        update_fields=["variance", "status", "matched_at", "matched_by", "rejection_reason", "updated_at"]
    )
    return invoice_match


def reject_invoice_match(invoice_match, reason=""):
    _assert_transition(invoice_match.status, InvoiceMatch.Status.REJECTED, INVOICE_MATCH_TRANSITIONS)
    if not reason:
        raise ValidationError("A rejection reason is required.")
    invoice_match.status = InvoiceMatch.Status.REJECTED
    invoice_match.rejection_reason = reason
    invoice_match.matched_at = timezone.now()
    invoice_match.matched_by = invoice_match.matched_by
    invoice_match.save(update_fields=["status", "rejection_reason", "matched_at", "updated_at"])
    return invoice_match


def decide_approval(approval, decision, actor=None, note=""):
    decision = (decision or "").lower()
    if decision not in ("approve", "approved", "reject", "rejected"):
        raise ValidationError("Decision must be approve or reject.")
    target = FinanceApproval.Status.APPROVED if decision.startswith("approve") else FinanceApproval.Status.REJECTED
    _assert_transition(approval.status, target, APPROVAL_TRANSITIONS)
    approval.status = target
    approval.approver = actor
    approval.decision_note = note
    approval.decided_at = timezone.now()
    approval.save(update_fields=["status", "approver", "decision_note", "decided_at", "updated_at"])
    return approval


def adjust_credit_limit(facility, new_limit):
    if facility.status != CreditFacility.Status.ACTIVE:
        raise ValidationError("Only active credit facilities can be adjusted.")
    new_limit = money(new_limit)
    if new_limit <= 0:
        raise ValidationError("Credit limit must be positive.")
    if new_limit < facility.drawn:
        raise ValidationError("New limit cannot be below the amount already drawn.")
    facility.limit = new_limit
    facility.save(update_fields=["limit", "updated_at"])
    return facility


def file_tax_assessment(assessment):
    if assessment.status != TaxAssessment.Status.DRAFT:
        raise ValidationError("Only draft tax assessments can be filed.")
    assessment.status = TaxAssessment.Status.FILED
    assessment.filed_at = timezone.now()
    assessment.save(update_fields=["status", "filed_at", "updated_at"])
    return assessment


def activate_credit_facility(facility):
    if facility.status != CreditFacility.Status.PENDING:
        raise ValidationError("Only pending facilities can be activated.")
    if facility.limit <= 0:
        raise ValidationError("Credit limit must be positive.")
    facility.status = CreditFacility.Status.ACTIVE
    facility.save(update_fields=["status", "updated_at"])
    return facility


def approve_credit_draw(draw):
    if draw.status != CreditDraw.Status.REQUESTED:
        raise ValidationError("Only requested draws can be approved.")
    facility = draw.facility
    if facility.status != CreditFacility.Status.ACTIVE:
        raise ValidationError("Facility is not active.")
    remaining = facility.limit - facility.drawn
    if draw.amount > remaining:
        raise ValidationError("Draw exceeds remaining credit.")
    draw.status = CreditDraw.Status.APPROVED
    draw.approved_at = timezone.now()
    draw.save(update_fields=["status", "approved_at", "updated_at"])
    facility.drawn = money(facility.drawn + draw.amount)
    facility.save(update_fields=["drawn", "updated_at"])
    return draw


def run_reconciliation(batch):
    totals = batch.items.aggregate(expected=Sum("expected_amount"), actual=Sum("actual_amount"))
    batch.expected_amount = money(totals["expected"])
    batch.actual_amount = money(totals["actual"])
    for item in batch.items.all():
        item.matched = item.expected_amount == item.actual_amount
        item.save(update_fields=["matched", "updated_at"])
    batch.status = ReconciliationBatch.Status.MATCHED
    batch.run_at = timezone.now()
    batch.save(update_fields=["expected_amount", "actual_amount", "status", "run_at", "updated_at"])
    return batch


def publish_statement(statement):
    if statement.status != FinanceStatement.Status.DRAFT:
        raise ValidationError("Only draft statements can be published.")
    statement.status = FinanceStatement.Status.PUBLISHED
    statement.published_at = timezone.now()
    statement.save(update_fields=["status", "published_at", "updated_at"])
    return statement
