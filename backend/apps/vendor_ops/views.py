from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    CustomerRelationshipNote,
    IncomingOrder,
    InventoryAdjustment,
    InventoryItem,
    PriceBookChange,
    PriceBookItem,
    PriceChangeRequest,
    ServiceRating,
    VendorAccount,
    VendorAnnouncement,
    VendorDispute,
    VendorDocument,
    VendorPayout,
    VendorPerformanceRecord,
    VendorReport,
    VendorRFQ,
    VendorScorecard,
    VendorTeamMembership,
)
from .serializers import (
    CustomerRelationshipNoteSerializer,
    IncomingOrderSerializer,
    InventoryAdjustmentSerializer,
    InventoryItemSerializer,
    PriceBookChangeSerializer,
    PriceBookItemSerializer,
    PriceChangeRequestSerializer,
    ServiceRatingSerializer,
    VendorAccountSerializer,
    VendorAnnouncementSerializer,
    VendorDisputeSerializer,
    VendorDocumentSerializer,
    VendorPayoutSerializer,
    VendorPerformanceRecordSerializer,
    VendorReportSerializer,
    VendorRFQSerializer,
    VendorScorecardSerializer,
    VendorTeamMembershipSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class VendorAccountViewSet(AuthenticatedViewSet):
    serializer_class = VendorAccountSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return VendorAccount.objects.all()
        return (
            VendorAccount.objects.filter(owner=user)
            | VendorAccount.objects.filter(team__user=user, team__is_active=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        vendor = self.get_object()
        if vendor.status != VendorAccount.Status.PENDING:
            raise ValidationError("Only pending vendor accounts can be activated.")
        vendor.status = VendorAccount.Status.ACTIVE
        vendor.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(vendor).data)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        vendor = self.get_object()
        if vendor.status != VendorAccount.Status.ACTIVE:
            raise ValidationError("Only active vendor accounts can be suspended.")
        vendor.status = VendorAccount.Status.SUSPENDED
        vendor.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(vendor).data)


class VendorTeamMembershipViewSet(AuthenticatedViewSet):
    queryset = VendorTeamMembership.objects.all()
    serializer_class = VendorTeamMembershipSerializer


class VendorPerformanceRecordViewSet(AuthenticatedViewSet):
    queryset = VendorPerformanceRecord.objects.select_related("vendor")
    serializer_class = VendorPerformanceRecordSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        record = wrap_service(services.publish_performance_record, self.get_object(), actor=request.user)
        return Response(self.get_serializer(record).data)


class VendorScorecardViewSet(AuthenticatedViewSet):
    queryset = VendorScorecard.objects.select_related("vendor")
    serializer_class = VendorScorecardSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        scorecard = wrap_service(services.submit_scorecard, self.get_object(), reviewer=request.user)
        return Response(self.get_serializer(scorecard).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        scorecard = wrap_service(services.approve_scorecard, self.get_object(), actor=request.user)
        return Response(self.get_serializer(scorecard).data)


class VendorDocumentViewSet(AuthenticatedViewSet):
    queryset = VendorDocument.objects.select_related("vendor")
    serializer_class = VendorDocumentSerializer

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        accept = str(request.data.get("accept", "true")).lower() not in ("0", "false", "no")
        document = wrap_service(
            services.verify_vendor_document,
            self.get_object(),
            reviewer=request.user,
            accept=accept,
            reason=request.data.get("reason", ""),
        )
        return Response(self.get_serializer(document).data)


class PriceChangeRequestViewSet(AuthenticatedViewSet):
    queryset = PriceChangeRequest.objects.select_related("price_book_item", "price_book_item__vendor")
    serializer_class = PriceChangeRequestSerializer

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        price_change = wrap_service(
            services.approve_price_change,
            self.get_object(),
            actor=request.user,
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(price_change).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        price_change = wrap_service(
            services.reject_price_change,
            self.get_object(),
            actor=request.user,
            reason=request.data.get("reason", ""),
        )
        return Response(self.get_serializer(price_change).data)


class VendorAnnouncementViewSet(AuthenticatedViewSet):
    queryset = VendorAnnouncement.objects.select_related("vendor")
    serializer_class = VendorAnnouncementSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        announcement = wrap_service(services.set_announcement_active, self.get_object(), True)
        return Response(self.get_serializer(announcement).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        announcement = wrap_service(services.set_announcement_active, self.get_object(), False)
        return Response(self.get_serializer(announcement).data)


class ServiceRatingViewSet(AuthenticatedViewSet):
    queryset = ServiceRating.objects.select_related("vendor")
    serializer_class = ServiceRatingSerializer

    @action(detail=True, methods=["post"])
    def hide(self, request, pk=None):
        rating = self.get_object()
        rating.is_public = False
        rating.save(update_fields=["is_public", "updated_at"])
        return Response(self.get_serializer(rating).data)


class InventoryItemViewSet(AuthenticatedViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        item = wrap_service(
            services.adjust_inventory,
            self.get_object(),
            request.data.get("delta", 0),
            reason=request.data.get("reason", ""),
            actor=request.user,
        )
        return Response(InventoryAdjustmentSerializer(item).data, status=status.HTTP_201_CREATED)


class InventoryAdjustmentViewSet(AuthenticatedViewSet):
    queryset = InventoryAdjustment.objects.all()
    serializer_class = InventoryAdjustmentSerializer


class PriceBookItemViewSet(AuthenticatedViewSet):
    queryset = PriceBookItem.objects.all()
    serializer_class = PriceBookItemSerializer


class PriceBookChangeViewSet(AuthenticatedViewSet):
    queryset = PriceBookChange.objects.all()
    serializer_class = PriceBookChangeSerializer


class IncomingOrderViewSet(AuthenticatedViewSet):
    queryset = IncomingOrder.objects.all()
    serializer_class = IncomingOrderSerializer

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        order = wrap_service(services.acknowledge_order, self.get_object())
        return Response(self.get_serializer(order).data)


class RFQViewSet(AuthenticatedViewSet):
    queryset = VendorRFQ.objects.all()
    serializer_class = VendorRFQSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        rfq = wrap_service(
            services.submit_rfq, self.get_object(), request.data.get("quoted_total")
        )
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def win(self, request, pk=None):
        rfq = wrap_service(services.mark_rfq_won, self.get_object())
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def lose(self, request, pk=None):
        rfq = wrap_service(services.mark_rfq_lost, self.get_object())
        return Response(self.get_serializer(rfq).data)


class CustomerRelationshipNoteViewSet(AuthenticatedViewSet):
    queryset = CustomerRelationshipNote.objects.all()
    serializer_class = CustomerRelationshipNoteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PayoutViewSet(AuthenticatedViewSet):
    queryset = VendorPayout.objects.all()
    serializer_class = VendorPayoutSerializer


class DisputeViewSet(AuthenticatedViewSet):
    queryset = VendorDispute.objects.all()
    serializer_class = VendorDisputeSerializer


class VendorReportViewSet(AuthenticatedViewSet):
    queryset = VendorReport.objects.all()
    serializer_class = VendorReportSerializer


class VendorDashboardView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    dashboard = staticmethod(services.incoming_work_dashboard)

    def get(self, request):
        vendor = wrap_service(services.vendor_for_user, request.user, request.query_params.get("vendor_id"))
        return Response(self.dashboard(vendor))


class IncomingWorkDashboardView(VendorDashboardView):
    dashboard = staticmethod(services.incoming_work_dashboard)


class InventoryDashboardView(VendorDashboardView):
    dashboard = staticmethod(services.inventory_dashboard)


class PayoutDashboardView(VendorDashboardView):
    dashboard = staticmethod(services.payout_dashboard)


class DisputeDashboardView(VendorDashboardView):
    dashboard = staticmethod(services.dispute_dashboard)


class SalesAnalyticsView(VendorDashboardView):
    dashboard = staticmethod(services.sales_analytics)
