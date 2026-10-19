from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BeneficialOwnerViewSet,
    ComplianceDocumentViewSet,
    CompliancePartyViewSet,
    CompliancePolicyViewSet,
    ComplianceTaskViewSet,
    CorrectiveActionViewSet,
    DataRetentionRequestViewSet,
    EvidenceFileViewSet,
    ExportComplianceCheckViewSet,
    IncidentRecordViewSet,
    InsuranceCertificateViewSet,
    KYBCaseViewSet,
    KYCCaseViewSet,
    QualityAuditViewSet,
    RiskAssessmentViewSet,
    RiskScoreViewSet,
    SanctionsEntryViewSet,
    SanctionsListViewSet,
    ScreeningCaseViewSet,
    SupplierDueDiligenceViewSet,
    TaxFormViewSet,
    WatchlistScreeningViewSet,
)

router = DefaultRouter()
router.register("parties", CompliancePartyViewSet)
router.register("screening-cases", ScreeningCaseViewSet)
router.register("compliance-tasks", ComplianceTaskViewSet)
router.register("risk-assessments", RiskAssessmentViewSet)
router.register("sanctions-lists", SanctionsListViewSet)
router.register("sanctions-entries", SanctionsEntryViewSet)
router.register("evidence-files", EvidenceFileViewSet)
router.register("risk-scores", RiskScoreViewSet)
router.register("kyb-cases", KYBCaseViewSet)
router.register("kyc-cases", KYCCaseViewSet, basename="kybcase")
router.register("beneficial-owners", BeneficialOwnerViewSet)
router.register("supplier-due-diligence", SupplierDueDiligenceViewSet)
router.register("documents", ComplianceDocumentViewSet)
router.register("watchlist-screenings", WatchlistScreeningViewSet)
router.register("policies", CompliancePolicyViewSet)
router.register("tax-forms", TaxFormViewSet)
router.register("insurance-certificates", InsuranceCertificateViewSet)
router.register("quality-audits", QualityAuditViewSet)
router.register("corrective-actions", CorrectiveActionViewSet)
router.register("incidents", IncidentRecordViewSet)
router.register("data-retention-requests", DataRetentionRequestViewSet)
router.register("export-checks", ExportComplianceCheckViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
