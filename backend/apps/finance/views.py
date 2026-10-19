from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    BankAccountSerializer,
    CreditDrawSerializer,
    CreditFacilitySerializer,
    EscrowAccountSerializer,
    EscrowHoldSerializer,
    ExpenseCategorySerializer,
    FinanceApprovalSerializer,
    FinanceStatementSerializer,
    InvoiceMatchSerializer,
    LedgerAccountSerializer,
    LedgerEntryDetailSerializer,
    LedgerEntrySerializer,
    PaymentRunDetailSerializer,
    PaymentRunSerializer,
    PayoutInstructionSerializer,
    ReconciliationBatchSerializer,
    ReconciliationItemSerializer,
    SettlementBatchSerializer,
    TaxAssessmentSerializer,
    TaxRegistrationSerializer,
    TransactionTagSerializer,
    WalletSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class WalletViewSet(AuthenticatedViewSet):
    serializer_class = WalletSerializer

    def get_queryset(self):
        qs = Wallet.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request, pk=None):
        return Response(services.wallet_balances(request.user))

    @action(detail=False, methods=["get"])
    def balances(self, request, pk=None):
        return Response(services.wallet_balances(request.user))


class LedgerAccountViewSet(AuthenticatedViewSet):
    queryset = LedgerAccount.objects.all()
    serializer_class = LedgerAccountSerializer


class TransactionTagViewSet(AuthenticatedViewSet):
    queryset = TransactionTag.objects.all()
    serializer_class = TransactionTagSerializer


class LedgerEntryViewSet(AuthenticatedViewSet):
    queryset = LedgerEntry.objects.prefetch_related("tags")
    serializer_class = LedgerEntrySerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LedgerEntryDetailSerializer
        return LedgerEntrySerializer

    @action(detail=True, methods=["get"])
    def post(self, request, pk=None):
        entry = wrap_service(services.post_ledger_entry, self.get_object(), actor=request.user)
        return Response(LedgerEntryDetailSerializer(entry).data)

    @action(detail=True, methods=["post"])
    def tag(self, request, pk=None):
        entry = self.get_object()
        tag_ids = request.data.get("tag_ids") or []
        tags = TransactionTag.objects.filter(pk__in=tag_ids, is_active=True)
        entry.tags.set(tags)
        return Response(LedgerEntryDetailSerializer(entry).data)


class EscrowAccountViewSet(AuthenticatedViewSet):
    queryset = EscrowAccount.objects.select_related("buyer_wallet", "seller_wallet")
    serializer_class = EscrowAccountSerializer

    @action(detail=True, methods=["post"])
    def fund(self, request, pk=None):
        escrow = wrap_service(services.fund_escrow, self.get_object(), request.data.get("amount"))
        return Response(self.get_serializer(escrow).data)

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        escrow = wrap_service(services.release_escrow, self.get_object())
        return Response(self.get_serializer(escrow).data)

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        escrow = wrap_service(services.refund_escrow, self.get_object())
        return Response(self.get_serializer(escrow).data)


class EscrowHoldViewSet(AuthenticatedViewSet):
    queryset = EscrowHold.objects.all()
    serializer_class = EscrowHoldSerializer


class SettlementBatchViewSet(AuthenticatedViewSet):
    queryset = SettlementBatch.objects.all()
    serializer_class = SettlementBatchSerializer

    @action(detail=True, methods=["post"])
    def settle(self, request, pk=None):
        batch = wrap_service(services.settle_batch, self.get_object())
        return Response(self.get_serializer(batch).data)


class PayoutInstructionViewSet(AuthenticatedViewSet):
    queryset = PayoutInstruction.objects.select_related("wallet", "settlement", "payment_run")
    serializer_class = PayoutInstructionSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        payout = wrap_service(services.approve_payout, self.get_object(), actor=request.user)
        return Response(self.get_serializer(payout).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        payout = wrap_service(services.send_payout, self.get_object())
        return Response(self.get_serializer(payout).data)


class BankAccountViewSet(AuthenticatedViewSet):
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        qs = BankAccount.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        account = wrap_service(services.verify_bank_account, self.get_object(), actor=request.user)
        return Response(self.get_serializer(account).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        account = wrap_service(services.deactivate_bank_account, self.get_object())
        return Response(self.get_serializer(account).data)


class PaymentRunViewSet(AuthenticatedViewSet):
    queryset = PaymentRun.objects.prefetch_related("payouts")
    serializer_class = PaymentRunSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentRunDetailSerializer
        return PaymentRunSerializer

    @action(detail=True, methods=["post"])
    def schedule(self, request, pk=None):
        payment_run = wrap_service(services.schedule_payment_run, self.get_object())
        return Response(PaymentRunDetailSerializer(payment_run).data)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        payment_run = wrap_service(services.execute_payment_run, self.get_object(), actor=request.user)
        return Response(PaymentRunDetailSerializer(payment_run).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        payment_run = wrap_service(services.cancel_payment_run, self.get_object())
        return Response(self.get_serializer(payment_run).data)


class ExpenseCategoryViewSet(AuthenticatedViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer


class InvoiceMatchViewSet(AuthenticatedViewSet):
    queryset = InvoiceMatch.objects.all()
    serializer_class = InvoiceMatchSerializer

    @action(detail=True, methods=["post"])
    def match(self, request, pk=None):
        invoice_match = wrap_service(
            services.match_invoice,
            self.get_object(),
            actor=request.user,
        )
        return Response(self.get_serializer(invoice_match).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        invoice_match = wrap_service(
            services.reject_invoice_match, self.get_object(), request.data.get("reason", "")
        )
        return Response(self.get_serializer(invoice_match).data)


class FinanceApprovalViewSet(AuthenticatedViewSet):
    queryset = FinanceApproval.objects.all()
    serializer_class = FinanceApprovalSerializer

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        approval = wrap_service(
            services.decide_approval,
            self.get_object(),
            request.data.get("decision", ""),
            actor=request.user,
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(approval).data)


class TaxRegistrationViewSet(AuthenticatedViewSet):
    queryset = TaxRegistration.objects.all()
    serializer_class = TaxRegistrationSerializer


class TaxAssessmentViewSet(AuthenticatedViewSet):
    queryset = TaxAssessment.objects.all()
    serializer_class = TaxAssessmentSerializer

    @action(detail=True, methods=["post"])
    def file(self, request, pk=None):
        assessment = wrap_service(services.file_tax_assessment, self.get_object())
        return Response(self.get_serializer(assessment).data)


class CreditFacilityViewSet(AuthenticatedViewSet):
    queryset = CreditFacility.objects.all()
    serializer_class = CreditFacilitySerializer

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        facility = wrap_service(services.activate_credit_facility, self.get_object())
        return Response(self.get_serializer(facility).data)

    @action(detail=True, methods=["post"])
    def adjust_limit(self, request, pk=None):
        facility = wrap_service(services.adjust_credit_limit, self.get_object(), request.data.get("new_limit"))
        return Response(self.get_serializer(facility).data)


class CreditDrawViewSet(AuthenticatedViewSet):
    queryset = CreditDraw.objects.select_related("facility")
    serializer_class = CreditDrawSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        draw = wrap_service(services.approve_credit_draw, self.get_object())
        return Response(self.get_serializer(draw).data)


class ReconciliationBatchViewSet(AuthenticatedViewSet):
    queryset = ReconciliationBatch.objects.prefetch_related("items")
    serializer_class = ReconciliationBatchSerializer

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        batch = wrap_service(services.run_reconciliation, self.get_object())
        return Response(self.get_serializer(batch).data)


class ReconciliationItemViewSet(AuthenticatedViewSet):
    queryset = ReconciliationItem.objects.all()
    serializer_class = ReconciliationItemSerializer


class FinanceStatementViewSet(AuthenticatedViewSet):
    queryset = FinanceStatement.objects.all()
    serializer_class = FinanceStatementSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        statement = wrap_service(services.publish_statement, self.get_object())
        return Response(self.get_serializer(statement).data)
