from rest_framework import serializers

from .models import (
    BankAccount,
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    ExpenseCategory,
    FinanceApproval,
    FinanceStatement,
    InvoiceMatch,
    LedgerAccount,
    LedgerEntry,
    PaymentRun,
    PayoutInstruction,
    ReconciliationBatch,
    ReconciliationItem,
    SettlementBatch,
    TaxAssessment,
    TaxRegistration,
    TransactionTag,
    Wallet,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


WalletSerializer = make(Wallet, extra=("available", "held"))
LedgerAccountSerializer = make(LedgerAccount)
TransactionTagSerializer = make(TransactionTag)
LedgerEntrySerializer = make(LedgerEntry, extra=("status", "posted_at", "posted_by"))
EscrowAccountSerializer = make(EscrowAccount, extra=("status",))
EscrowHoldSerializer = make(EscrowHold, extra=("status",))
SettlementBatchSerializer = make(SettlementBatch, extra=("status", "settled_at", "net_amount"))
PayoutInstructionSerializer = make(PayoutInstruction, extra=("status", "sent_at", "payment_run"))
BankAccountSerializer = make(BankAccount, extra=("verified", "verified_at", "verifed_by"))
PaymentRunSerializer = make(PaymentRun, extra=("reference", "status", "total_amount", "executed_at", "executed_by"))
ExpenseCategorySerializer = make(ExpenseCategory)
InvoiceMatchSerializer = make(InvoiceMatch, extra=("reference", "status", "variance", "matched_at", "matched_by"))
FinanceApprovalSerializer = make(FinanceApproval, extra=("status", "decided_at", "approver"))
TaxRegistrationSerializer = make(TaxRegistration)
TaxAssessmentSerializer = make(TaxAssessment, extra=("status", "filed_at"))
CreditFacilitySerializer = make(CreditFacility, extra=("status", "drawn"))
CreditDrawSerializer = make(CreditDraw, extra=("status", "approved_at"))
ReconciliationBatchSerializer = make(ReconciliationBatch, extra=("status", "run_at"))
ReconciliationItemSerializer = make(ReconciliationItem)
FinanceStatementSerializer = make(FinanceStatement, extra=("status", "published_at"))


class PaymentRunDetailSerializer(PaymentRunSerializer):
    payouts = PayoutInstructionSerializer(many=True, read_only=True)

    class Meta(PaymentRunSerializer.Meta):
        fields = "__all__"
        read_only_fields = PaymentRunSerializer.Meta.read_only_fields


class LedgerEntryDetailSerializer(LedgerEntrySerializer):
    tags = TransactionTagSerializer(many=True, read_only=True)

    class Meta(LedgerEntrySerializer.Meta):
        fields = "__all__"
        read_only_fields = LedgerEntrySerializer.Meta.read_only_fields
