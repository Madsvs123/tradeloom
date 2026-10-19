from djang.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    ApprovalRuleSerializer,
    ApprovalWorkflowSerializer,
    BudgetLineSerializer,
    BuyingCommitteeMemberSerializer,
    BuyingCommitteeSerializer,
    ContractCoverageCheckSerializer,
    DepartmentBudgetSerializer,
    PolicyRuleSerializer,
    PreferredSupplierProgramSerializer,
    ProcurementEventSerializer,
    PurchaseRequisitionLineSerializer,
    PurchaseRequisitionSerializer,
    PurchasingPolicySerializer,
    RequisitionToRFQConversionSerializer,
    SavingsTrackingSerializer,
    SourcingRequestSerializer,
    SpendCategorySerializer,
    SpendControlSerializer,
    SupplierOnboardingChecklistSerializer,
    SupplierScorecardSerializer,
    SupplierSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class DepartmentBudgetViewSet(AuthenticatedViewSet):
    queryset = DepartmentBudget.objects.all()
    serializer_class = DepartmentBudgetSerializer


class PurchasingPolicyViewSet(AuthenticatedViewSet):
    queryset = PurchasingPolicy.objects.all()
    serializer_class = PurchasingPolicySerializer


class ApprovalRuleViewSet(AuthenticatedViewSet):
    queryset = ApprovalRule.objects.all()
    serializer_class = ApprovalRuleSerializer


class PreferredSupplierProgramViewSet(AuthenticatedViewSet):
    queryset = PreferredSupplierProgram.objects.all()
    serializer_class = PreferredSupplierProgramSerializer


class SupplierViewSet(AuthenticatedViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class SupplierOnboardingViewSet(AuthenticatedViewSet):
    queryset = SupplierOnboardingChecklist.objects.select_related("supplier")
    serializer_class = SupplierOnboardingChecklistSerializer

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        checklist = wrap_service(services.complete_onboarding, self.get_object())
        return Response(self.get_serializer(checklist).data)


class SupplierScorecardViewSet(AuthenticatedViewSet):
    queryset = SupplierScorecard.objects.all()
    serializer_class = SupplierScorecardSerializer


class BuyingCommitteeViewSet(AuthenticatedViewSet):
    queryset = BuyingCommittee.objects.all()
    serializer_class = BuyingCommitteeSerializer


class BuyingCommitteeMemberViewSet(AuthenticatedViewSet):
    queryset = BuyingCommitteeMember.objects.all()
    serializer_class = BuyingCommitteeMemberSerializer


class PurchaseRequisitionViewSet(AuthenticatedViewSet):
    serializer_class = PurchaseRequisitionSerializer

    def get_queryset(self):
        qs = PurchaseRequisition.objects.prefetch_related("lines")
        if self.request.user.is_staff:
            return qs
        return qs.filter(requester=self.request.user, status=PurchaseRequisition.Status.APPROVED)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user, number=services._number())

    @action(detail=True, methods=["put"])
    def submit(self, request, pk=None):
        requisition = wrap_service(services.submit_requisition, self.get_object(), actor=request.user)
        return Response(self.get_serializer(requisition).data)

    @action(detail=True, methods=["post"], url_path="convert-to-rfq")
    def convert_to_rfq(self, request, pk=None):
        conversion = wrap_service(
            services.convert_to_rfq, self.get_object(), actor=request.user, notes=request.data.get("notes", "")
        )
        return Response(RequisitionToRFQConversionSerializer(conversion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def policy_rules(self, request, pk=None):
        rules = wrap_service(services.evaluate_policy, self.get_object())
        return Response(PolicyRuleSerializer(rules, many=True).data)


class PurchaseRequisitionLineViewSet(AuthenticatedViewSet):
    queryset = PurchaseRequisitionLine.objects.all()
    serializer_class = PurchaseRequisitionLineSerializer

    def perform_create(self, serializer):
        line = serializer.save()
        services.recalculate_requisition(line.requisition)


class ApprovalWorkflowViewSet(AuthenticatedViewSet):
    queryset = ApprovalWorkflow.objects.select_related("requisition")
    serializer_class = ApprovalWorkflowSerializer

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        workflow = wrap_service(
            services.decide_workflow,
            self.get_object(),
            request.data.get("decision", ""),
            actor=request.user,
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(workflow).data)


class RequisitionToRFQConversionViewSet(AuthenticatedViewSet):
    queryset = RequisitionToRFQConversion.objects.all()
    serializer_class = RequisitionToRFQConversionSerializer


class ProcurementEventViewSet(AuthenticatedViewSet):
    queryset = ProcurementEvent.objects.all()
    serializer_class = ProcurementEventSerializer


class SpendControlViewSet(AuthenticatedViewSet):
    queryset = SpendControl.objects.all()
    serializer_class = SpendControlSerializer


class SourcingRequestViewSet(AuthenticatedViewSet):
    serializer_class = SourcingRequestSerializer

    def get_queryset(self):
        qs = SourcingRequest.objects.select_related("requester", "category")
        if self.request.user.is_staff:
            return qs
        return qs.filter(requester=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        sourcing_request = wrap_service(services.submit_sourcing_request, self.get_object())
        return Response(self.get_serializer(sourcing_request).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        sourcing_request = wrap_service(services.start_sourcing, self.get_object())
        return Response(self.get_serializer(sourcing_request).data)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        sourcing_request = wrap_service(services.convert_sourcing_request, self.get_object())
        return Response(self.get_serializer(sourcing_request).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        sourcing_request = wrap_service(services.cancel_sourcing_request, self.get_object())
        return Response(self.get_serializer(sourcing_request).data)


class BudgetLineViewSet(AuthenticatedViewSet):
    serializer_class = BudgetLineSerializer

    def get_queryset(self):
        qs = BudgetLine.objects.select_related("budget", "category")
        budget_id = self.request.query_params.get("budget")
        if budget_id:
            qs = qs.filter(budget_id=budget_id)
        return qs

    @action(detail=True, methods=["post"])
    def commit(self, request, pk=None):
        budget_line = wrap_service(
            services.commit_budget_line, self.get_object(), request.data.get("amount", 0)
        )
        return Response(self.get_serializer(budget_line).data)

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        budget_line = wrap_service(
            services.release_budget_line, self.get_object(), request.data.get("amount", 0)
        )
        return Response(self.get_serializer(budget_line).data)

    @action(detail=True, methods=["post"])
    def spend(self, request, pk=None):
        budget_line = wrap_service(
            services.spend_budget_line, self.get_object(), request.data.get("amount", 0)
        )
        return Response(self.get_serializer(budget_line).data)


class PolicyRuleViewSet(AuthenticatedViewSet):
    serializer_class = PolicyRuleSerializer

    def get_queryset(self):
        qs = PolicyRule.objects.select_related("policy", "category")
        policy_id = self.request.query_params.get("policy")
        if policy_id:
            qs = qs.filter(policy_id=policy_id)
        return qs


class ContractCoverageCheckViewSet(AuthenticatedViewSet):
    serializer_class = ContractCoverageCheckSerializer

    def get_queryset(self):
        qs = ContractCoverageCheck.objects.select_related("requisition", "checked_by")
        requisition_id = self.request.query_params.get("requisition")
        if requisition_id:
            qs = qs.filter(requisition_id=requisition_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user)


class SpendCategoryViewSet(AuthenticatedViewSet):
    queryset = SpendCategory.objects.select_related("parent")
    serializer_class = SpendCategorySerializer


class SavingsTrackingViewSet(AuthenticatedViewSet):
    serializer_class = SavingsTrackingSerializer

    def get_queryset(self):
        qs = SavingsTracking.objects.select_related("category", "requisition", "owner")
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def realize(self, request, pk=None):
        savings = wrap_service(
            services.realize_savings,
            self.get_object(),
            request.data.get("realized_amount"),
        )
        return Response(self.get_serializer(savings).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        savings = wrap_service(services.void_savings, self.get_object())
        return Response(self.get_serializer(savings).data)
