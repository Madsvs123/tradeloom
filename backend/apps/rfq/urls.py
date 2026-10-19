from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EvaluationCriterionViewSet,
    EvaluationScoreViewSet,
    NegotiationMessageViewSet,
    NegotiationRoomViewSet,
    QuotationComparisonSnapshotViewSet,
    RFQAttachmentViewSet,
    RFQDocumentViewSet,
    RFQViewSet,
    RfqTemplateViewSet,
    SupplierCounterOfferViewSet,
    SupplierQuotationViewSet,
)

router = DefaultRouter()
router.register("rfqs", RFQViewSet, basename="rfq")
router.register("quotes", SupplierQuotationViewSet, basename="rfq-quotation")
router.register("negotiation-messages", NegotiationMessageViewSet, basename="rfq-negotiation-message")
router.register("counteroffers", SupplierCounterOfferViewSet, basename="rfq-counteroffer")
router.register("attachments", RFQAttachmentViewSet, basename="rfq-attachment")
router.register("templates", RfqTemplateViewSet, basename="rfq-template")
router.register("evaluation-criteria", EvaluationCriterionViewSet, basename="rfq-evaluation-criterion")
router.register("evaluation-scores", EvaluationScoreViewSet, basename="rfq-evaluation-score")
router.register("comparison-snapshots", QuotationComparisonSnapshotViewSet, basename="rfq-comparison-snapshot")
router.register("documents", RFQDocumentViewSet, basename="rfq-document")
router.register("negotiation-rooms", NegotiationRoomViewSet, basename="rfq-negotiation-room")

urlpatterns = [
    path("", include(router.urls)),
]
