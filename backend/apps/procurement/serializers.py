from rest_framework import serializers

from .models import (
    ApprovalRule,
    ApprovalWorkflow,
    BudgetLine,
    BuyingCommittee,
    BuyingCommitteeMember,
    ContractCoverageCheck,
    DepartmentBudget,
    PolicyRule,
    PreferredSupplierProgram,
    ProcurementEvent,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchasingPolicy,
    RequisitionToRFQConversion,
    SavingsTracking,
    SourcingRequest,
    SpendCategory,
    SpendControl,
    Supplier,
    SupplierOnboardingChecklist,
    SupplierScorecard,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


DepartmentBudgetSerializer = make(DepartmentBudget)
PurchasingPolicySerializer = make(PurchasingPolicy)
ApprovalRuleSerializer = make(ApprovalRule)
PreferredSupplierProgramSerializer = make(PreferredSupplierProgram)
SupplierSerializer = make(Supplier)
SupplierOnboardingChecklistSerializer = make(SupplierOnboardingChecklist, extra=("status", "completed_at"))
SupplierScorecardSerializer = make(SupplierScorecard)
BuyingCommitteeSerializer = make(BuyingCommittee)
BuyingCommitteeMemberSerializer = make(BuyingCommitteeMember)
PurchaseRequisitionLineSerializer = make(PurchaseRequisitionLine)


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    lines = PurchaseRequisitionLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = "__all__"
        read_only_fields = ("id", "number", "requester", "status", "total", "created_at", "updated_at")


ApprovalWorkflowSerializer = make(ApprovalWorkflow, extra=("status", "decided_at"))
RequisitionToRFQConversionSerializer = make(RequisitionToRFQConversion)
ProcurementEventSerializer = make(ProcurementEvent)
SpendControlSerializer = make(SpendControl)

SourcingRequestSerializer = make(SourcingRequest, extra=("reference", "status"))
BudgetLineSerializer = make(BudgetLine, extra=("spent",))
PolicyRuleSerializer = make(PolicyRule)
ContractCoverageCheckSerializer = make(ContractCoverageCheck)
SpendCategorySerializer = make(SpendCategory)
SavingsTrackingSerializer = make(SavingsTracking, extra=("reference", "status", "realized_at"))
