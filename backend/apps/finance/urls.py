from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BankAccountViewSet,
    CreditDrawViewSet,
    CreditFacilityViewSet,
    EscrowAccountViewSet,
    EscrowHoldViewSet,
    ExpenseCategoryViewSet,
    FinanceApprovalViewSet,
    FinanceStatementViewSet,
    InvoiceMatchViewSet,
    LedgerAccountViewSet,
    LedgerEntryViewSet,
    PaymentRunViewSet,
    PayoutInstructionViewSet,
    ReconciliationBatchViewSet,
    ReconciliationItemViewSet,
    SettlementBatchViewSet,
    TaxAssessmentViewSet,
    TaxRegistrationViewSet,
    TransactionTagViewSet,
    WalletViewSet,
)

router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallet")
router.register("ledger-accounts", LedgerAccountViewSet)
router.register("transaction-tags", TransactionTagViewSet)
router.register("ledger-entries", LedgerEntryViewSet)
router.register("escrow-accounts", EscrowAccountViewSet)
router.register("escrow-holds", EscrowHoldViewSet)
router.register("settlement-batches", SettlementBatchViewSet)
router.register("payment-runs", PaymentRunViewSet)
router.register("payouts", PayoutInstructionViewSet)
router.register("bank-accounts", BankAccountViewSet)
router.register("expense-categories", ExpenseCategoryViewSet)
router.register("invoice-matches", InvoiceMatchViewSet)
router.register("approvals", FinanceApprovalViewSet)
router.register("tax-registrations", TaxRegistrationViewSet)
router.register("tax-assessments", TaxAssessmentViewSet)
router.register("credit-facilities", CreditFacilityViewSet)
router.register("credit-draws", CreditDrawViewSet)
router.register("reconciliation-batches", ReconciliationBatchViewSet)
router.register("reconciliation-items", ReconciliationItemViewSet)
router.register("statements", FinanceStatementViewSet)

urlpatterns = [
    path("v2/", include(router.urls)),
]
