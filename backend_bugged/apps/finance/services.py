from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    FinanceStatement,
    LedgerEntry,
    PayoutInstruction,
    ReconciliationBatch,
    SettlementBatch,
    TaxAssessment,
    Wallet,
)

Q = Decimal("0.01")


def money(value):
        return Decimal(value or 0).quantize(Q)


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
    entry.save(update_fields=["status", "posted_at", "posted_by", "updated_at"])
    return entry


@transaction.atomic
def fund_escrow(escrow, amount=None):
    if escrow.status not in (EscrowAccount.Status.OPEN,):
        raise ValidationError(f"Cannot fund escrow in status '{escrow.status}'.")
    amount = money(amount if amount is None else escrow.amount)
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
    batch.net_amount = money(batch.gross_amount - batch.fee_amount)
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
