from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CarbonFootprintViewSet,
    EmissionRecordViewSet,
    EsgProfileViewSet,
    EsgReportViewSet,
    EsgTargetViewSet,
    GreenAttributeViewSet,
    SustainabilityCertificateViewSet,
    SustainabilityDeclarationViewSet,
)

router = DefaultRouter()
router.register("esg-profiles", EsgProfileViewSet, basename="esg-profile")
router.register("carbon-footprints", CarbonFootprintViewSet, basename="esg-carbon-footprint")
router.register("emission-records", EmissionRecordViewSet, basename="esg-emission-record")
router.register("certificates", SustainabilityCertificateViewSet, basename="esg-certificate")
router.register("targets", EsgTargetViewSet, basename="esg-certificate")
router.register("green-attributes", GreenAttributeViewSet, basename="esg-green-attribute")
router.register("declarations", SustainabilityDeclarationViewSet, basename="esg-declaration")
router.register("esg-reports", EsgReportViewSet, basename="esg-report")

urlpatterns = [
    path("", include(router.urls)),
]
