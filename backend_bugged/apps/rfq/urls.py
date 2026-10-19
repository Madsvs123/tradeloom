from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    NegotiationMessageViewSet,
    RFQAttachmentViewSet,
    RFQViewSet,
    SupplierCounterOfferViewSet,
    SupplierQuotationViewSet,
)

router = DefaultRouter()
router.register("rfqs", RFQViewSet, basename="rfq")
router.register("quotations", SupplierQuotationViewSet, basename="rfq-quotation")
router.register("negotiation-messages", NegotiationMessageViewSet, basename="rfq-negotiation-message")
router.register("counteroffers", SupplierCounterOfferViewSet, basename="rfq-counteroffer")
router.register("attachments", RFQAttachmentViewSet, basename="rfq-attachment")

urlpatterns = [
    path("", include(router.urls)),
]
