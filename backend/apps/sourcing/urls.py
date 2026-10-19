from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuctionBidViewSet,
    BidEvaluationViewSet,
    BidLineItemViewSet,
    BidPackageViewSet,
    EvaluationCriterionViewSet,
    ReverseAuctionViewSet,
    SourcingProjectViewSet,
    SupplierInvitationViewSet,
    TenderDocumentViewSet,
    TenderLotViewSet,
    TenderResponseViewSet,
    TenderViewSet,
)

router = DefaultRouter()
router.register("sourcing-projects", SourcingProjectViewSet, basename="sourcing-project")
router.register("tenders", TenderViewSet, basename="sourcing-tender")
router.register("tender-lots", TenderLotViewSet, basename="sourcing-tender-lot")
router.register("tender-documents", TenderDocumentViewSet, basename="sourcing-tender-document")
router.register("bid-packages", BidPackageViewSet, basename="sourcing-bid-package")
router.register("tender-responses", TenderResponseViewSet, basename="sourcing-tender-response")
router.register("bid-line-items", BidLineItemViewSet, basename="sourcing-bid-line-item")
router.register("evaluation-criteria", EvaluationCriterionViewSet, basename="sourcing-evaluation-criterion")
router.register("bid-evaluations", BidEvaluationViewSet, basename="sourcing-bid-evaluation")
router.register("reverse-auctions", ReverseAuctionViewSet, basename="sourcing-reverse-auction")
router.register("auction-bids", AuctionBidViewSet, basename="sourcing-auction-bid")
router.register("supplier-invitations", SupplierInvitationViewSet, basename="sourcing-supplier-invitation")

urlpatterns = [
    path("", include(router.urls)),
]
