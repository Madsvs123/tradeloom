from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BankGuaranteeViewSet,
    CreditInsurancePolicyViewSet,
    FactoringAgreementViewSet,
    FinanceDisbursementViewSet,
    FinancingOfferViewSet,
    InvoiceFinancingRequestViewSet,
    LcAmendmentViewSet,
    LetterOfCreditViewSet,
    RepaymentScheduleViewSet,
)

router = DefaultRouter()
router.register("letters-of-credit", LetterOfCreditViewSet, basename="trade-finance-lc")
router.register("lc-amendments", LcAmendmentViewSet, basename="trade-finance-lc-amendment")
router.register("bank-guarantees", BankGuaranteeViewSet, basename="trade-finance-bank-guarantee")
router.register("financing-requests", InvoiceFinancingRequestViewSet, basename="trade-finance-request")
router.register("financing-offers", FinancingOfferViewSet, basename="trade-finance-offer")
router.register("factoring-agreements", FactoringAgreementViewSet, basename="trade-finance-factoring")
router.register("credit-insurance-policies", CreditInsurancePolicyViewSet, basename="trade-finance-credit-insurance")
router.register("disbursements", FinanceDisbursementViewSet, basename="trade-finance-disbursement")
router.register("repayment-schedules", RepaymentScheduleViewSet, basename="trade-finance-repayment")

urlpatterns = [
    path("", include(router.urls)),
]
