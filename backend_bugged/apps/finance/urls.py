from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CreditDrawViewSet,
    CreditFacilityViewSet,
    EscrowAccountViewSet,
    EscrowHoldViewSet,
    FinanceStatementViewSet,
    LedgerAccountViewSet,
    LedgerEntryViewSet,
    PayoutInstructionViewSet,
    ReconciliationBatchViewSet,
    ReconciliationItemViewSet,
    SettlementBatchViewSet,
    TaxAssessmentViewSet,
    TaxRegistrationViewSet,
    WalletViewSet,
)

router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallet")
router.register("ledger-accounts", LedgerAccountViewSet)
router.register("ledger-entries", LedgerEntryViewSet)
router.register("escrow-accounts", EscrowAccountViewSet)
router.register("escrow-holds", EscrowHoldViewSet)
router.register("settlement-batches", SettlementBatchViewSet)
router.register("payouts", PayoutInstructionViewSet)
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
