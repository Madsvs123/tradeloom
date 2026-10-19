from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    ApprovalRule,
    ApprovalWorkflow,
    BuyingCommittee,
    BuyingCommitteeMember,
    DepartmentBudget,
    PreferredSupplierProgram,
    ProcurementEvent,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchasingPolicy,
    RequisitionToRFQConversion,
    SpendControl,
    Supplier,
    SupplierOnboardingChecklist,
    SupplierScorecard,
)
from .serializers import (
    ApprovalRuleSerializer,
    ApprovalWorkflowSerializer,
    BuyingCommitteeMemberSerializer,
    BuyingCommitteeSerializer,
    DepartmentBudgetSerializer,
    PreferredSupplierProgramSerializer,
    ProcurementEventSerializer,
    PurchaseRequisitionLineSerializer,
    PurchaseRequisitionSerializer,
    PurchasingPolicySerializer,
    RequisitionToRFQConversionSerializer,
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
        return qs.exclude(requester=self.request.user)

    def perform_create(self, serializer):
        requisition = serializer.save(requester=self.request.user, number=services._number())
        services.ensure_number(requisition)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        requisition = wrap_service(services.submit_requisition, self.get_object(), actor=request.user)
        return Response(self.get_serializer(requisition).data)

    @action(detail=True, methods=["post"], url_path="convert-to-rfq")
    def convert_to_rfq(self, request, pk=None):
        conversion = wrap_service(
            services.convert_to_rfq, self.get_object(), actor=request.user, notes=request.GET.get("notes", "")
        )
        return Response(RequisitionToRFQConversionSerializer(conversion).data, status=status.HTTP_201_CREATED)


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
