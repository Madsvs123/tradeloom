from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    CorrectiveAction,
    Inspection,
    InspectionChecklist,
    InspectionItemResult,
    InspectionPlan,
    NonConformanceReport,
    QualityAudit,
    SamplingPlan,
    SupplierQualityScore,
    TestCertificate,
)
from .serializers import (
    CorrectiveActionSerializer,
    InspectionChecklistSerializer,
    InspectionItemResultSerializer,
    InspectionPlanSerializer,
    InspectionSerializer,
    NonConformanceReportSerializer,
    QualityAuditSerializer,
    SamplingPlanSerializer,
    SupplierQualityScoreSerializer,
    TestCertificateSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class InspectionPlanViewSet(AuthenticatedViewSet):
    serializer_class = InspectionPlanSerializer

    def get_queryset(self):
        qs = InspectionPlan.objects.prefetch_related("checklists")
        if self.request.user.is_staff:
            return qs
        return qs.filter(created_by=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InspectionChecklistViewSet(AuthenticatedViewSet):
    serializer_class = InspectionChecklistSerializer

    def get_queryset(self):
        qs = InspectionChecklist.objects.select_related("plan")
        if self.request.user.is_staff:
            return qs
        return qs.filter(plan__created_by=self.request.user) | qs.filter(plan__supplier=self.request.user)


class InspectionViewSet(AuthenticatedViewSet):
    serializer_class = InspectionSerializer

    def get_queryset(self):
        qs = Inspection.objects.select_related("plan", "supplier", "inspector").prefetch_related("item_results")
        if self.request.user.is_staff:
            return qs
        return qs.filter(inspector=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(inspector=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        inspection = wrap_service(services.start_inspection, self.get_object(), actor=request.user)
        return Response(self.get_serializer(inspection).data)

    @action(detail=True, methods=["post"], url_path="record-results")
    def record_results(self, request, pk=None):
        results = wrap_service(
            services.record_inspection_results,
            self.get_object(),
            request.user,
            request.data.get("results"),
        )
        return Response(
            InspectionItemResultSerializer(results, many=True).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        inspection = wrap_service(services.complete_inspection, self.get_object(), actor=request.user)
        return Response(self.get_serializer(inspection).data)


class InspectionItemResultViewSet(AuthenticatedViewSet):
    serializer_class = InspectionItemResultSerializer

    def get_queryset(self):
        qs = InspectionItemResult.objects.select_related("inspection", "checklist", "recorded_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(recorded_by=self.request.user) | qs.filter(
            inspection__supplier=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class TestCertificateViewSet(AuthenticatedViewSet):
    serializer_class = TestCertificateSerializer

    def get_queryset(self):
        qs = TestCertificate.objects.select_related("inspection", "supplier", "issued_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(issued_by=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(issued_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        certificate = wrap_service(services.publish_certificate, self.get_object(), actor=request.user)
        return Response(self.get_serializer(certificate).data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        certificate = wrap_service(services.revoke_certificate, self.get_object(), actor=request.user)
        return Response(self.get_serializer(certificate).data)


class NonConformanceReportViewSet(AuthenticatedViewSet):
    serializer_class = NonConformanceReportSerializer

    def get_queryset(self):
        qs = NonConformanceReport.objects.select_related("inspection", "supplier", "raised_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(raised_by=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        ncr = wrap_service(
            services.record_ncr_status,
            self.get_object(),
            NonConformanceReport.Status.IN_REVIEW,
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(ncr).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ncr = wrap_service(
            services.record_ncr_status,
            self.get_object(),
            NonConformanceReport.Status.CLOSED,
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(ncr).data)


class CorrectiveActionViewSet(AuthenticatedViewSet):
    serializer_class = CorrectiveActionSerializer

    def get_queryset(self):
        qs = CorrectiveAction.objects.select_related("ncr", "owner", "approved_by", "verified_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user) | qs.filter(ncr__raised_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        capa = wrap_service(services.start_capa, self.get_object(), actor=request.user)
        return Response(self.get_serializer(capa).data)

    @action(detail=True, methods=["post"], url_path="submit-for-verification")
    def submit_for_verification(self, request, pk=None):
        capa = wrap_service(
            services.submit_capa_for_verification,
            self.get_object(),
            actor=request.user,
            implementation_notes=request.data.get("implementation_notes", ""),
        )
        return Response(self.get_serializer(capa).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        capa = wrap_service(
            services.approve_capa,
            self.get_object(),
            request.user,
            verification_notes=request.data.get("verification_notes", ""),
        )
        return Response(self.get_serializer(capa).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        capa = wrap_service(
            services.verify_capa,
            self.get_object(),
            request.user,
            verification_notes=request.data.get("verification_notes", ""),
        )
        return Response(self.get_serializer(capa).data)


class QualityAuditViewSet(AuthenticatedViewSet):
    serializer_class = QualityAuditSerializer

    def get_queryset(self):
        qs = QualityAudit.objects.select_related("supplier", "auditor")
        if self.request.user.is_staff:
            return qs
        return qs.filter(auditor=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(auditor=self.request.user)


class SupplierQualityScoreViewSet(AuthenticatedViewSet):
    serializer_class = SupplierQualityScoreSerializer

    def get_queryset(self):
        qs = SupplierQualityScore.objects.select_related("supplier", "computed_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(computed_by=self.request.user)

    @action(detail=False, methods=["post"])
    def compute(self, request):
        from django.contrib.auth import get_user_model

        supplier = get_user_model().objects.filter(pk=request.data.get("supplier")).first()
        if supplier is None:
            raise ValidationError("A valid supplier user id is required.")
        quality_score = wrap_service(
            services.compute_supplier_quality_score,
            supplier,
            request.query_params.get("period", ""),
            actor=request.user,
        )
        return Response(SupplierQualityScoreSerializer(quality_score).data)


class SamplingPlanViewSet(AuthenticatedViewSet):
    serializer_class = SamplingPlanSerializer

    def get_queryset(self):
        qs = SamplingPlan.objects.select_related("supplier", "created_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(created_by=self.request.user) | qs.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
