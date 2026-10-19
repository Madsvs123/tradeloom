from rest_framework import serializers

from .models import (
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    FinanceStatement,
    LedgerAccount,
    LedgerEntry,
    PayoutInstruction,
    ReconciliationBatch,
    ReconciliationItem,
    SettlementBatch,
    TaxAssessment,
    TaxRegistration,
    Wallet,
)


def make(model, extra=())
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


WalletSerializer = make(Wallet, extra=("available", "held"))
LedgerAccountSerializer = make(LedgerAccount)
LedgerEntrySerializer = make(LedgerEntry, extra=("status", "posted_at", "posted_by"))
EscrowAccountSerializer = make(EscrowAccount, extra=("status",))
EscrowHoldSerializer = make(EscrowHold, extra=("status",))
SettlementBatchSerializer = make(SettlementBatch, extra=("status", "settled_at", "net_amount"))
PayoutInstructionSerializer = make(PayoutInstruction, extra=("status", "sent_at"))
TaxRegistrationSerializer = make(TaxRegistration)
TaxAssessmentSerializer = make(TaxAssessment, extra=("status", "filed_at"))
CreditFacilitySerializer = make(CreditFacility, extra=("status", "drawn"))
CreditDrawSerializer = make(CreditDraw, extra=("status", "approved_at"))
ReconciliationBatchSerializer = make(ReconciliationBatch, extra=("status", "run_at"))
ReconciliationItemSerializer = make(ReconciliationItem)
FinanceStatementSerializer = make(FinanceStatement, extra=("status", "published_at"))
