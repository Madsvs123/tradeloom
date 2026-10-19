from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    BeneficialOwner,
    ComplianceDocument,
    ComplianceParty,
    CompliancePolicy,
    ComplianceTask,
    CorrectiveAction,
    DataRetentionRequest,
    EvidenceFile,
    ExportComplianceCheck,
    IncidentRecord,
    InsuranceCertificate,
    KYBCase,
    KYCCase,
    QualityAudit,
    RiskAssessment,
    RiskScore,
    SanctionsEntry,
    SanctionsList,
    ScreeningCase,
    SupplierDueDiligence,
    TaxForm,
    WatchlistScreening,
)
from .serializers import (
    BeneficialOwnerSerializer,
    ComplianceDocumentSerializer,
    CompliancePartyDetailSerializer,
    CompliancePartySerializer,
    CompliancePolicySerializer,
    ComplianceTaskSerializer,
    CorrectiveActionSerializer,
    DataRetentionRequestSerializer,
    EvidenceFileSerializer,
    ExportComplianceCheckSerializer,
    IncidentRecordSerializer,
    InsuranceCertificateSerializer,
    KYBCaseSerializer,
    KYCCaseSerializer,
    QualityAuditSerializer,
    RiskAssessmentSerializer,
    RiskScoreSerializer,
    SanctionsEntrySerializer,
    SanctionsListSerializer,
    ScreeningCaseSerializer,
    SupplierDueDiligenceSerializer,
    TaxFormSerializer,
    WatchlistScreeningSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class CompliancePartyViewSet(AuthenticatedViewSet):
    queryset = ComplianceParty.objects.prefetch_related("beneficial_owners", "documents")
    serializer_class = CompliancePartySerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CompliancePartyDetailSerializer
        return CompliancePartySerializer

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        parties = self.get_queryset()
        return Response([services.party_summary(party) for party in parties[:100]])

    @action(detail=True, methods=["get"])
    def structure(self, request, pk=None):
        return Response(services.party_structure(self.get_object()))

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


class ScreeningCaseViewSet(AuthenticatedViewSet):
    queryset = ScreeningCase.objects.select_related("party")
    serializer_class = ScreeningCaseSerializer

    @action(detail=True, methods=["post"])
    def start_review(self, request, pk=None):
        case = wrap_service(services.start_screening_review, self.get_object(), actor=request.user)
        return Response(self.get_serializer(case).data)

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        case = wrap_service(
            services.decide_screening_case,
            self.get_object(),
            request.data.get("decision", ""),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(case).data)


class ComplianceTaskViewSet(AuthenticatedViewSet):
    queryset = ComplianceTask.objects.all()
    serializer_class = ComplianceTaskSerializer

    def perform_create(self, serializer):
        serializer.save(assignee=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        task = wrap_service(services.start_task, self.get_object(), actor=request.user)
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = wrap_service(services.complete_task, self.get_object())
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        task = wrap_service(services.cancel_task, self.get_object())
        return Response(self.get_serializer(task).data)


class RiskAssessmentViewSet(AuthenticatedViewSet):
    queryset = RiskAssessment.objects.select_related("party")
    serializer_class = RiskAssessmentSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        assessment = wrap_service(services.submit_risk_assessment, self.get_object())
        return Response(self.get_serializer(assessment).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        assessment = wrap_service(services.approve_risk_assessment, self.get_object(), actor=request.user)
        return Response(self.get_serializer(assessment).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        assessment = wrap_service(
            services.reject_risk_assessment,
            self.get_object(),
            actor=request.user,
            reason=request.data.get("reason", ""),
        )
        return Response(self.get_serializer(assessment).data)


class SanctionsListViewSet(AuthenticatedViewSet):
    queryset = SanctionsList.objects.all()
    serializer_class = SanctionsListSerializer


class SanctionsEntryViewSet(AuthenticatedViewSet):
    queryset = SanctionsEntry.objects.select_related("sanctions_list", "matched_case")
    serializer_class = SanctionsEntrySerializer

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        entry = self.get_object()
        case_id = request.data.get("case_id")
        case = ScreeningCase.objects.filter(pk=case_id).first() if case_id else None
        entry = wrap_service(services.decide_sanctions_entry, entry, request.data.get("decision", ""), case=case)
        return Response(self.get_serializer(entry).data)


class EvidenceFileViewSet(AuthenticatedViewSet):
    queryset = EvidenceFile.objects.all()
    serializer_class = EvidenceFileSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


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

    @action(detail=False, methods=["get"], url_path="expiry-check")
    def expiry_check(self, request):
        days = int(request.query_params.get("days", 30) or 30)
        return Response({"days": days, "documents": services.check_document_expiry(days)})


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
