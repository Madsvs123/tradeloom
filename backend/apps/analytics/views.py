from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    AnalyticsSnapshot,
    AnomalyAlert,
    CohortSummary,
    ComparisonPeriod,
    Dashboard,
    DashboardWidget,
    ExecutiveScorecard,
    ExportJob,
    ExportSubscription,
    ForecastModel,
    ForecastProjection,
    KpiDefinition,
    MetricDefinition,
    OrderCycleTimeMetric,
    ReportBuilderDefinition,
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
    ComparisonPeriodSerializer,
    DashboardSerializer,
    DashboardWidgetSerializer,
    ExecutiveScorecardSerializer,
    ExportJobSerializer,
    ExportSubscriptionSerializer,
    ForecastModelDetailSerializer,
    ForecastModelSerializer,
    ForecastProjectionSerializer,
    KpiDefinitionSerializer,
    MetricDefinitionSerializer,
    OrderCycleTimeMetricSerializer,
    ReportBuilderDefinitionSerializer,
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


class KpiDefinitionViewSet(AuthenticatedViewSet):
    queryset = KpiDefinition.objects.all()
    serializer_class = KpiDefinitionSerializer

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        kpi = self.get_object()
        kpi.is_active = True
        kpi.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(kpi).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        kpi = self.get_object()
        kpi.is_active = False
        kpi.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(kpi).data)


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

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        report = wrap_service(services.run_report, self.get_object())
        return Response(self.get_serializer(report).data)


class ReportBuilderDefinitionViewSet(AuthenticatedViewSet):
    queryset = ReportBuilderDefinition.objects.all()
    serializer_class = ReportBuilderDefinitionSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        builder = wrap_service(services.publish_report_builder, self.get_object())
        return Response(self.get_serializer(builder).data)


class ExportJobViewSet(AuthenticatedViewSet):
    queryset = ExportJob.objects.select_related("owner", "report")
    serializer_class = ExportJobSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        job = wrap_service(services.run_export_job, self.get_object(), actor=request.user)
        return Response(self.get_serializer(job).data)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        job = wrap_service(services.retry_export_job, self.get_object())
        return Response(self.get_serializer(job).data)


class ReportScheduleViewSet(AuthenticatedViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer


class AnalyticsSnapshotViewSet(AuthenticatedViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer


class ComparisonPeriodViewSet(AuthenticatedViewSet):
    queryset = ComparisonPeriod.objects.all()
    serializer_class = ComparisonPeriodSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def compute(self, request, pk=None):
        comparison = wrap_service(services.compute_comparison, self.get_object())
        return Response(self.get_serializer(comparison).data)


class ForecastModelViewSet(AuthenticatedViewSet):
    queryset = ForecastModel.objects.prefetch_related("projections")
    serializer_class = ForecastModelSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ForecastModelDetailSerializer
        return ForecastModelSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def train(self, request, pk=None):
        model = wrap_service(services.train_forecast_model, self.get_object(), actor=request.user)
        return Response(ForecastModelDetailSerializer(model).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        model = wrap_service(services.activate_forecast_model, self.get_object())
        return Response(self.get_serializer(model).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        model = wrap_service(services.archive_forecast_model, self.get_object())
        return Response(self.get_serializer(model).data)


class ForecastProjectionViewSet(AuthenticatedViewSet):
    queryset = ForecastProjection.objects.select_related("model")
    serializer_class = ForecastProjectionSerializer

    @action(detail=True, methods=["post"], url_path="record-actual")
    def record_actual(self, request, pk=None):
        projection = wrap_service(
            services.record_actual_projection, self.get_object(), request.data.get("actual_value")
        )
        return Response(self.get_serializer(projection).data)


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

    @action(detail=True, methods=["post"])
    def payload(self, request, pk=None):
        return Response(services.scorecard_payload(self.get_object()))

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        scorecard = wrap_service(services.publish_scorecard, self.get_object())
        return Response(self.get_serializer(scorecard).data)
