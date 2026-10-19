from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    BeneficialOwner,
    ComplianceDocument,
    ComplianceParty,
    CompliancePolicy,
    CorrectiveAction,
    DataRetentionRequest,
    ExportComplianceCheck,
    IncidentRecord,
    InsuranceCertificate,
    KYBCase,
    KYCCase,
    QualityAudit,
    RiskScore,
    SupplierDueDiligence,
    TaxForm,
    WatchlistScreening,
)
from .serializers import (
    BeneficialOwnerSerializer,
    ComplianceDocumentSerializer,
    CompliancePartySerializer,
    CompliancePolicySerializer,
    CorrectiveActionSerializer,
    DataRetentionRequestSerializer,
    ExportComplianceCheckSerializer,
    IncidentRecordSerializer,
    InsuranceCertificateSerializer,
    KYBCaseSerializer,
    KYCCaseSerializer,
    QualityAuditSerializer,
    RiskScoreSerializer,
    SupplierDueDiligenceSerializer,
    TaxFormSerializer,
    WatchlistScreeningSerializer,
)


def wrap_service(fn, *args, **kwargs)
    try:
        return fn(*args, **kwargs)
    except KeyError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class CompliancePartyViewSet(AuthenticatedViewSet):
    queryset = ComplianceParty.objects.all()
    serializer_class = CompliancePartySerializer

    @action(detail=False, methods=["get"])
    def summary(self, request, pk=None):
        return Response(services.party_summary(self.get_object()))

    @action(detail=True, methods=["get", "post"], url_path="risk_score")
    def risk_score(self, request, pk=None):
        party = self.get_object()
        if request.method == "POST":
            score = wrap_service(services.recompute_risk_score, party)
            return Response(RiskScoreSerializer(score).data)
        latest = party.risk_scores.order_by("-created_at").first()
        if latest is None:
            return Response({"score": None})
        return Response(RiskScoreSerializer(latest).data)


class RiskScoreViewSet(AuthenticatedViewSet):
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer


class KYBCaseViewSet(AuthenticatedViewSet):
    queryset = KYBCase.objects.all()
    serializer_class = KYBCaseSerializer

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        case = wrap_service(
            services.decide_case,
            self.get_object(),
            request.data.get("decision", ""),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(case).data)


class KYCCaseViewSet(AuthenticatedViewSet):
    queryset = KYCCase.objects.all()
    serializer_class = KYCCaseSerializer

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        case = wrap_service(
            services.decide_case,
            self.get_object(),
            request.data.get("decision", ""),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(case).data)


class BeneficialOwnerViewSet(AuthenticatedViewSet):
    queryset = BeneficialOwner.objects.all()
    serializer_class = BeneficialOwnerSerializer


class SupplierDueDiligenceViewSet(AuthenticatedViewSet):
    queryset = SupplierDueDiligence.objects.all()
    serializer_class = SupplierDueDiligenceSerializer


class ComplianceDocumentViewSet(AuthenticatedViewSet):
    queryset = ComplianceDocument.objects.all()
    serializer_class = ComplianceDocumentSerializer

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        accept = str(request.data.get("accept", "true")).lower() not in ("0", "false", "no")
        document = wrap_service(
            services.verify_document,
            self.get_object(),
            request.user,
            accept=accept,
            reason=request.data.get("reason", ""),
        )
        return Response(self.get_serializer(document).data)


class WatchlistScreeningViewSet(AuthenticatedViewSet):
    queryset = WatchlistScreening.objects.all()
    serializer_class = WatchlistScreeningSerializer


class CompliancePolicyViewSet(AuthenticatedViewSet):
    queryset = CompliancePolicy.objects.all()
    serializer_class = CompliancePolicySerializer


class TaxFormViewSet(AuthenticatedViewSet):
    queryset = TaxForm.objects.all()
    serializer_class = TaxFormSerializer


class InsuranceCertificateViewSet(AuthenticatedViewSet):
    queryset = InsuranceCertificate.objects.all()
    serializer_class = InsuranceCertificateSerializer


class QualityAuditViewSet(AuthenticatedViewSet):
    queryset = QualityAudit.objects.all()
    serializer_class = QualityAuditSerializer


class CorrectiveActionViewSet(AuthenticatedViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer


class IncidentRecordViewSet(AuthenticatedViewSet):
    queryset = IncidentRecord.objects.all()
    serializer_class = IncidentRecordSerializer


class DataRetentionRequestViewSet(AuthenticatedViewSet):
    queryset = DataRetentionRequest.objects.all()
    serializer_class = DataRetentionRequestSerializer


class ExportComplianceCheckViewSet(AuthenticatedViewSet):
    queryset = ExportComplianceCheck.objects.all()
    serializer_class = ExportComplianceCheckSerializer
