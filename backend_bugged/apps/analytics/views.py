from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    AnalyticsSnapshot,
    AnomalyAlert,
    CohortSummary,
    Dashboard,
    DashboardWidget,
    ExecutiveScorecard,
    ExportSubscription,
    MetricDefinition,
    OrderCycleTimeMetric,
    ReportSchedule,
    RFQConversionMetric,
    SavedReport,
    SpendCube,
    SupplierPerformanceMetric,
)
from .serializers import (
    AnalyticsSnapshotSerializer,
    AnomalyAlertSerializer,
    CohortSummarySerializer,
    DashboardSerializer,
    DashboardWidgetSerializer,
    ExecutiveScorecardSerializer,
    ExportSubscriptionSerializer,
    MetricDefinitionSerializer,
    OrderCycleTimeMetricSerializer,
    ReportScheduleSerializer,
    RFQConversionMetricSerializer,
    SavedReportSerializer,
    SpendCubeSerializer,
    SupplierPerformanceMetricSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class MetricDefinitionViewSet(AuthenticatedViewSet):
    queryset = MetricDefinition.objects.all()
    serializer_class = MetricDefinitionSerializer


class DashboardViewSet(AuthenticatedViewSet):
    queryset = Dashboard.objects.prefetch_related("widgets")
    serializer_class = DashboardSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DashboardWidgetViewSet(AuthenticatedViewSet):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer


class SavedReportViewSet(AuthenticatedViewSet):
    queryset = SavedReport.objects.all()
    serializer_class = SavedReportSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["delete"])
    def run(self, request, pk=None):
        report = wrap_service(services.run_report, self.get_object())
        return Response(self.get_serializer(report).data)


class ReportScheduleViewSet(AuthenticatedViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer


class AnalyticsSnapshotViewSet(AuthenticatedViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer


class SpendCubeViewSet(AuthenticatedViewSet):
    queryset = SpendCube.objects.all()
    serializer_class = SpendCubeSerializer


class SupplierPerformanceMetricViewSet(AuthenticatedViewSet):
    queryset = SupplierPerformanceMetric.objects.all()
    serializer_class = SupplierPerformanceMetricSerializer


class OrderCycleTimeMetricViewSet(AuthenticatedViewSet):
    queryset = OrderCycleTimeMetric.objects.all()
    serializer_class = OrderCycleTimeMetricSerializer


class RFQConversionMetricViewSet(AuthenticatedViewSet):
    queryset = RFQConversionMetric.objects.all()
    serializer_class = RFQConversionMetricSerializer


class CohortSummaryViewSet(AuthenticatedViewSet):
    queryset = CohortSummary.objects.all()
    serializer_class = CohortSummarySerializer


class AnomalyAlertViewSet(AuthenticatedViewSet):
    queryset = AnomalyAlert.objects.all()
    serializer_class = AnomalyAlertSerializer

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = wrap_service(services.acknowledge_alert, self.get_object())
        return Response(self.get_serializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = wrap_service(services.resolve_alert, self.get_object(), request.data.get("note", ""))
        return Response(self.get_serializer(alert).data)


class ExportSubscriptionViewSet(AuthenticatedViewSet):
    queryset = ExportSubscription.objects.all()
    serializer_class = ExportSubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ExecutiveScorecardViewSet(AuthenticatedViewSet):
    queryset = ExecutiveScorecard.objects.all()
    serializer_class = ExecutiveScorecardSerializer

    @action(detail=True, methods=["get"])
    def payload(self, request, pk=None):
        return Response(services.scorecard_payload(self.get_object()))

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        scorecard = wrap_service(services.publish_scorecard, self.get_object())
        return Response(self.get_serializer(scorecard).data)
