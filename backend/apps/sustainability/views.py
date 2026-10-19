from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    CarbonFootprint,
    EmissionRecord,
    EsgProfile,
    EsgReport,
    EsgTarget,
    GreenAttribute,
    SustainabilityCertificate,
    SustainabilityDeclaration,
)
from .serializers import (
    CarbonFootprintSerializer,
    EmissionRecordSerializer,
    EsgProfileSerializer,
    EsgReportSerializer,
    EsgTargetSerializer,
    GreenAttributeSerializer,
    SustainabilityCertificateSerializer,
    SustainabilityDeclarationSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class EsgProfileViewSet(AuthenticatedViewSet):
    serializer_class = EsgProfileSerializer

    def get_queryset(self):
        qs = EsgProfile.objects.prefetch_related("carbon_footprints", "targets", "certificates")
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        profile = wrap_service(services.publish_profile, self.get_object(), actor=request.user)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        profile = wrap_service(services.archive_profile, self.get_object(), actor=request.user)
        return Response(self.get_serializer(profile).data)


class CarbonFootprintViewSet(AuthenticatedViewSet):
    serializer_class = CarbonFootprintSerializer

    def get_queryset(self):
        qs = CarbonFootprint.objects.select_related("profile").prefetch_related("emission_records")
        if self.request.user.is_staff:
            return qs
        return qs.filter(profile__owner=self.request.user)

    @action(detail=True, methods=["post"])
    def compute(self, request, pk=None):
        footprint = wrap_service(services.compute_footprint_totals, self.get_object())
        return Response(self.get_serializer(footprint).data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        footprint = wrap_service(services.publish_footprint, self.get_object(), actor=request.user)
        return Response(self.get_serializer(footprint).data)


class EmissionRecordViewSet(AuthenticatedViewSet):
    serializer_class = EmissionRecordSerializer

    def get_queryset(self):
        qs = EmissionRecord.objects.select_related("footprint__profile")
        if self.request.user.is_staff:
            return qs
        return qs.filter(footprint__profile__owner=self.request.user)


class SustainabilityCertificateViewSet(AuthenticatedViewSet):
    serializer_class = SustainabilityCertificateSerializer

    def get_queryset(self):
        qs = SustainabilityCertificate.objects.select_related("profile")
        if self.request.user.is_staff:
            return qs
        return qs.filter(profile__owner=self.request.user)


class EsgTargetViewSet(AuthenticatedViewSet):
    serializer_class = EsgTargetSerializer

    def get_queryset(self):
        qs = EsgTarget.objects.select_related("profile")
        if self.request.user.is_staff:
            return qs
        return qs.filter(profile__owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="update-progress")
    def update_progress(self, request, pk=None):
        target = wrap_service(
            services.update_target_progress, self.get_object(), request.data.get("current_value")
        )
        return Response(self.get_serializer(target).data)


class GreenAttributeViewSet(AuthenticatedViewSet):
    serializer_class = GreenAttributeSerializer

    def get_queryset(self):
        qs = GreenAttribute.objects.select_related("profile", "verified_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(profile__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        attribute = self.get_object()
        attribute.verification_status = GreenAttribute.VerificationStatus.THIRD_PARTY_VERIFIED
        attribute.verified_by = request.user
        attribute.verified_at = timezone.now()
        attribute.save(
            update_fields=["verification_status", "verified_by", "verified_at", "updated_at"]
        )
        return Response(self.get_serializer(attribute).data)


class SustainabilityDeclarationViewSet(AuthenticatedViewSet):
    serializer_class = SustainabilityDeclarationSerializer

    def get_queryset(self):
        qs = SustainabilityDeclaration.objects.select_related("profile", "declared_by", "verified_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(declared_by=self.request.user) | qs.filter(profile__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(declared_by=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        declaration = wrap_service(services.submit_declaration, self.get_object(), actor=request.user)
        return Response(self.get_serializer(declaration).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        approved = bool(request.data.get("approved", False))
        declaration = wrap_service(
            services.verify_declaration,
            self.get_object(),
            request.user,
            approved,
            verification_notes=request.data.get("verification_notes", ""),
        )
        return Response(self.get_serializer(declaration).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        declaration = wrap_service(services.withdraw_declaration, self.get_object(), actor=request.user)
        return Response(self.get_serializer(declaration).data)


class EsgReportViewSet(AuthenticatedViewSet):
    serializer_class = EsgReportSerializer

    def get_queryset(self):
        qs = EsgReport.objects.select_related("profile", "generated_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(profile__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        report = self.get_object()
        if report.status != EsgReport.Status.DRAFT:
            raise ValidationError("Only draft reports can be published.")
        report.status = EsgReport.Status.PUBLISHED
        report.published_at = timezone.now()
        report.save(update_fields=["status", "published_at", "updated_at"])
        return Response(self.get_serializer(report).data)
