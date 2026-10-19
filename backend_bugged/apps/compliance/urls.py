from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    BeneficialOwnerViewSet,
    ComplianceDocumentViewSet,
    CompliancePartyViewSet,
    CompliancePolicyViewSet,
    CorrectiveActionViewSet,
    DataRetentionRequestViewSet,
    ExportComplianceCheckViewSet,
    IncidentRecordViewSet,
    InsuranceCertificateViewSet,
    KYBCaseViewSet,
    KYCCaseViewSet,
    QualityAuditViewSet,
    RiskScoreViewSet,
    SupplierDueDiligenceViewSet,
    TaxFormViewSet,
    WatchlistScreeningViewSet,
)

router = DefaultRouter()
router.register("parties", CompliancePartyViewSet)
router.register("risk-scores", RiskScoreViewSet)
router.register("kyb-cases", KYBCaseViewSet)
router.register("kyc-cases", KYCCaseViewSet)
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
