from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CorrectiveActionViewSet,
    InspectionChecklistViewSet,
    InspectionItemResultViewSet,
    InspectionPlanViewSet,
    InspectionViewSet,
    NonConformanceReportViewSet,
    QualityAuditViewSet,
    SamplingPlanViewSet,
    SupplierQualityScoreViewSet,
    TestCertificateViewSet,
)

router = DefaultRouter()
router.register("inspection-plans", InspectionPlanViewSet, basename="quality-inspection-plan")
router.register("inspections", InspectionViewSet, basename="quality-inspection")
router.register("inspection-checklists", InspectionChecklistViewSet, basename="quality-inspection-checklist")
router.register("inspection-item-results", InspectionItemResultViewSet, basename="quality-inspection-item-result")
router.register("test-certificates", TestCertificateViewSet, basename="quality-test-certificate")
router.register("ncr", NonConformanceReportViewSet, basename="quality-ncr")
router.register("capa", CorrectiveActionViewSet, basename="quality-capa")
router.register("quality-audits", QualityAuditViewSet, basename="quality-audit")
router.register("supplier-quality-scores", SupplierQualityScoreViewSet, basename="quality-supplier-score")
router.register("sampling-plans", SamplingPlanViewSet, basename="quality-sampling-plan")

urlpatterns = [
    path("", include(router.urls)),
]
