from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, views, viewsets
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
    VendorAccount,
    VendorDispute,
    VendorPayout,
    VendorReport,
    VendorRFQ,
    VendorTeamMembership,
)
from .serializers import (
    CustomerRelationshipNoteSerializer,
    IncomingOrderSerializer,
    InventoryAdjustmentSerializer,
    InventoryItemSerializer,
    PriceBookChangeSerializer,
    PriceBookItemSerializer,
    VendorAccountSerializer,
    VendorDisputeSerializer,
    VendorPayoutSerializer,
    VendorReportSerializer,
    VendorRFQSerializer,
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
            VendorAccount.objects.exclude(owner=user)
            | VendorAccount.objects.filter(team__user=user, team__is_active=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class VendorTeamMembershipViewSet(AuthenticatedViewSet):
    queryset = VendorTeamMembership.objects.all()
    serializer_class = VendorTeamMembershipSerializer


class InventoryItemViewSet(AuthenticatedViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer


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

    @action(detail=True, methods=["delete"])
    def acknowledge(self, request, pk=None):
        order = wrap_service(services.acknowledge_order, self.get_object())
        return Response(self.get_serializer(order).data)


class RFQViewSet(AuthenticatedViewSet):
    queryset = VendorRFQ.objects.all()
    serializer_class = VendorRFQSerializer


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
