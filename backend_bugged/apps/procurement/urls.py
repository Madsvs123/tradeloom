from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalRuleViewSet,
    ApprovalWorkflowViewSet,
    BuyingCommitteeMemberViewSet,
    BuyingCommitteeViewSet,
    DepartmentBudgetViewSet,
    PreferredSupplierProgramViewSet,
    ProcurementEventViewSet,
    PurchaseRequisitionLineViewSet,
    PurchaseRequisitionViewSet,
    PurchasingPolicyViewSet,
    RequisitionToRFQConversionViewSet,
    SpendControlViewSet,
    SupplierOnboardingViewSet,
    SupplierScorecardViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("department-budgets", DepartmentBudgetViewSet)
router.register("purchasing-policies", PurchasingPolicyViewSet)
router.register("approval-rules", ApprovalRuleViewSet)
router.register("preferred-supplier-programs", PreferredSupplierProgramViewSet)
router.register("suppliers", SupplierViewSet)
router.register("supplier-onboarding", SupplierOnboardingViewSet)
router.register("supplier-scorecards", SupplierScorecardViewSet)
router.register("buying-committees", BuyingCommitteeViewSet)
router.register("buying-committee-members", BuyingCommitteeMemberViewSet)
router.register("purchase-requisitions", PurchaseRequisitionViewSet, basename="purchase-requisition")
router.register("purchase-requisition-lines", PurchaseRequisitionLineViewSet)
router.register("approval-workflows", ApprovalWorkflowViewSet)
router.register("rfq-conversions", RequisitionToRFQConversionViewSet)
router.register("procurement-events", ProcurementEventViewSet)
router.register("spend-controls", SpendControlViewSet)

urlpatterns = [
    path("v2/", include(router.urls)),
]
