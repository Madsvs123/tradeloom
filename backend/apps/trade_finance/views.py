from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    BankGuarantee,
    CreditInsurancePolicy,
    FactoringAgreement,
    FinanceDisbursement,
    FinancingOffer,
    InvoiceFinancingRequest,
    LcAmendment,
    LetterOfCredit,
    RepaymentSchedule,
)
from .serializers import (
    BankGuaranteeSerializer,
    CreditInsurancePolicySerializer,
    FactoringAgreementSerializer,
    FinanceDisbursementSerializer,
    FinancingOfferSerializer,
    InvoiceFinancingRequestSerializer,
    LcAmendmentSerializer,
    LetterOfCreditSerializer,
    RepaymentScheduleSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class LetterOfCreditViewSet(AuthenticatedViewSet):
    serializer_class = LetterOfCreditSerializer

    def get_queryset(self):
        qs = LetterOfCredit.objects.select_related("applicant", "beneficiary").prefetch_related("amendments")
        if self.request.user.is_staff:
            return qs
        return qs.filter(applicant=self.request.user) | qs.filter(beneficiary=self.request.user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        lc = wrap_service(services.issue_lc, self.get_object(), actor=request.user)
        return Response(self.get_serializer(lc).data)

    @action(detail=True, methods=["post"])
    def amend(self, request, pk=None):
        amendment = wrap_service(
            services.request_lc_amendment,
            self.get_object(),
            request.user,
            request.data.get("amendment_type", ""),
            description=request.data.get("description", ""),
            new_amount=request.data.get("new_amount"),
            new_expiry_date=request.data.get("new_expiry_date"),
        )
        return Response(LcAmendmentSerializer(amendment).data, status=status.HTTP_201_CREATED)


class LcAmendmentViewSet(AuthenticatedViewSet):
    serializer_class = LcAmendmentSerializer

    def get_queryset(self):
        qs = LcAmendment.objects.select_related("lc", "requested_by", "approved_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(lc__applicant=self.request.user) | qs.filter(lc__beneficiary=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        amendment = wrap_service(services.approve_lc_amendment, self.get_object(), request.user)
        return Response(self.get_serializer(amendment).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        amendment = wrap_service(services.reject_lc_amendment, self.get_object(), actor=request.user)
        return Response(self.get_serializer(amendment).data)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        amendment = wrap_service(services.apply_lc_amendment, self.get_object(), actor=request.user)
        return Response(self.get_serializer(amendment).data)


class BankGuaranteeViewSet(AuthenticatedViewSet):
    serializer_class = BankGuaranteeSerializer

    def get_queryset(self):
        qs = BankGuarantee.objects.select_related("applicant", "beneficiary")
        if self.request.user.is_staff:
            return qs
        return qs.filter(applicant=self.request.user) | qs.filter(beneficiary=self.request.user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        guarantee = wrap_service(services.issue_guarantee, self.get_object(), actor=request.user)
        return Response(self.get_serializer(guarantee).data)


class InvoiceFinancingRequestViewSet(AuthenticatedViewSet):
    serializer_class = InvoiceFinancingRequestSerializer

    def get_queryset(self):
        qs = InvoiceFinancingRequest.objects.select_related("applicant").prefetch_related(
            "offers", "disbursements", "repayment_schedules"
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(applicant=self.request.user) | qs.filter(
            offers__offered_by=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        request_obj = wrap_service(services.submit_financing_request, self.get_object(), actor=request.user)
        return Response(self.get_serializer(request_obj).data)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        approved = bool(request.data.get("approved", True))
        request_obj = wrap_service(
            services.review_financing_request,
            self.get_object(),
            actor=request.user,
            approved=approved,
        )
        return Response(self.get_serializer(request_obj).data)

    @action(detail=True, methods=["post"])
    def offer(self, request, pk=None):
        offer = wrap_service(
            services.make_offer,
            self.get_object(),
            request.user,
            request.data.get("amount"),
            request.data.get("rate"),
            tenor_days=request.data.get("tenor_days", 30),
            fees=request.data.get("fees", 0),
            valid_until=request.data.get("valid_until"),
        )
        return Response(FinancingOfferSerializer(offer).data, status=status.HTTP_201_CREATED)


class FinancingOfferViewSet(AuthenticatedViewSet):
    serializer_class = FinancingOfferSerializer

    def get_queryset(self):
        qs = FinancingOffer.objects.select_related("request", "offered_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(offered_by=self.request.user) | qs.filter(request__applicant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(offered_by=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        offer = wrap_service(services.accept_offer, self.get_object(), actor=request.user)
        return Response(self.get_serializer(offer).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        offer = wrap_service(services.decline_offer, self.get_object(), actor=request.user)
        return Response(self.get_serializer(offer).data)


class FinanceDisbursementViewSet(AuthenticatedViewSet):
    serializer_class = FinanceDisbursementSerializer

    def get_queryset(self):
        qs = FinanceDisbursement.objects.select_related("request", "agreement", "recipient")
        if self.request.user.is_staff:
            return qs
        return qs.filter(recipient=self.request.user) | qs.filter(
            request__applicant=self.request.user
        ) | qs.filter(agreement__supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def fund(self, request, pk=None):
        disbursement = wrap_service(services.fund_disbursement, self.get_object(), actor=request.user)
        return Response(self.get_serializer(disbursement).data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        disbursement = wrap_service(
            services.fail_disbursement,
            self.get_object(),
            request.data.get("reason", ""),
            actor=request.user,
        )
        return Response(self.get_serializer(disbursement).data)


class RepaymentScheduleViewSet(AuthenticatedViewSet):
    serializer_class = RepaymentScheduleSerializer

    def get_queryset(self):
        qs = RepaymentSchedule.objects.select_related("request", "paid_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(request__applicant=self.request.user)

    @action(detail=True, methods=["post"], url_path="record-repayment")
    def record_repayment(self, request, pk=None):
        schedule = wrap_service(
            services.record_repayment,
            self.get_object(),
            request.user,
            request.data.get("payment_amount"),
        )
        return Response(self.get_serializer(schedule).data)


class FactoringAgreementViewSet(AuthenticatedViewSet):
    serializer_class = FactoringAgreementSerializer

    def get_queryset(self):
        qs = FactoringAgreement.objects.select_related("supplier", "factor")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(factor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        agreement = wrap_service(services.activate_factoring_agreement, self.get_object(), actor=request.user)
        return Response(self.get_serializer(agreement).data)


class CreditInsurancePolicyViewSet(AuthenticatedViewSet):
    serializer_class = CreditInsurancePolicySerializer

    def get_queryset(self):
        qs = CreditInsurancePolicy.objects.select_related("insured")
        if self.request.user.is_staff:
            return qs
        return qs.filter(insured=self.request.user)

    def perform_create(self, serializer):
        serializer.save(insured=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        policy = wrap_service(services.activate_policy, self.get_object(), actor=request.user)
        return Response(self.get_serializer(policy).data)
