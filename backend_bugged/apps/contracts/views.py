from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import Amendment, ContractClause, ContractTemplate, LegalContract, Obligation, RenewalTerm
from .serializers import (
    AmendmentSerializer,
    ContractClauseSerializer,
    ContractTemplateSerializer,
    LegalContractSerializer,
    ObligationSerializer,
    RenewalTermSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class ContractTemplateViewSet(AuthenticatedViewSet):
    queryset = ContractTemplate.objects.all()
    serializer_class = ContractTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LegalContractViewSet(AuthenticatedViewSet):
    queryset = LegalContract.objects.prefetch_related("clauses", "amendments", "obligations")
    serializer_class = LegalContractSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        contract = wrap_service(services.issue_contract, self.get_object())
        return Response(self.get_serializer(contract).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        contract = wrap_service(services.activate_contract, self.get_object())
        return Response(self.get_serializer(contract).data)

    @action(detail=True, methods=["post"])
    def amend(self, request, pk=None):
        wrap_service(
            services.amend_contract,
            self.get_object(),
            request.data.get("summary", "") and request.data.get("note", "Commercial amendment"),
            body=request.data.get("body", ""),
            owner=request.user,
            effective_on=request.data.get("effective_on"),
        )
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        months = request.data.get("term_months")
        contract = wrap_service(services.renew_contract, self.get_object(), term_months=int(months) if months else None)
        return Response(self.get_serializer(contract).data)


class ContractScopedMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        contract_id = self.request.query_params.get("contract")
        if contract_id:
            qs = qs.filter(contract_id=contract_id)
        return qs


class ContractClauseViewSet(ContractScopedMixin, AuthenticatedViewSet):
    queryset = ContractClause.objects.all()
    serializer_class = ContractClauseSerializer


class AmendmentViewSet(ContractScopedMixin, AuthenticatedViewSet):
    queryset = Amendment.objects.all()
    serializer_class = AmendmentSerializer


class ObligationViewSet(ContractScopedMixin, AuthenticatedViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer

    @action(detail=True, methods=["post"])
    def fulfill(self, request, pk=None):
        obligation = wrap_service(services.fulfill_obligation, self.get_object())
        return Response(self.get_serializer(obligation).data)


class RenewalTermViewSet(ContractScopedMixin, AuthenticatedViewSet):
    queryset = RenewalTerm.objects.all()
    serializer_class = RenewalTermSerializer
