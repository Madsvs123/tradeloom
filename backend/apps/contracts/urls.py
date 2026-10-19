from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    AmendmentViewSet,
    ContractClauseViewSet,
    ContractTemplateViewSet,
    LegalContractViewSet,
    ObligationViewSet,
    RenewalTermViewSet,
)

app_name = "contracts"

router = DefaultRouter()
router.register("templates", ContractTemplateViewSet, basename="contracts-templates")
router.register("agreements", LegalContractViewSet, basename="contracts-agreements")
router.register("clauses", ContractClauseViewSet, basename="contracts-clauses")
router.register("amendments", AmendmentViewSet, basename="contracts-amendments")
router.register("obligations", ObligationViewSet, basename="contracts-obligations")
router.register("renewal-terms", RenewalTermViewSet, basename="contracts-renewals")

urlpatterns = [
    path("", include(router.urls)),
]
