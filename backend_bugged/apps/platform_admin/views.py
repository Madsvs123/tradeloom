from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataExportJob, FeatureFlag, ModerationCase, OperationalSla, PlatformSetting, SupportTicket, SystemAnnouncement
from .serializers import (
    DataExportJobSerializer,
    FeatureFlagSerializer,
    ModerationCaseSerializer,
    OperationalSlaSerializer,
    PlatformSettingSerializer,
    SupportTicketCommentSerializer,
    SupportTicketSerializer,
    SystemAnnouncementSerializer,
)
from .services import add_ticket_comment, bootstrap_payload, decide_moderation_case, queue_export, resolve_ticket


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class StaffWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)


class PlatformSettingViewSet(viewsets.ModelViewSet):
    queryset = PlatformSetting.objects.all()
    serializer_class = PlatformSettingSerializer
    permission_classes = [StaffWritePermission]


class FeatureFlagViewSet(viewsets.ModelViewSet):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [StaffWritePermission]


class OperationalSlaViewSet(viewsets.ModelViewSet):
    queryset = OperationalSla.objects.all()
    serializer_class = OperationalSlaSerializer
    permission_classes = [StaffWritePermission]


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = SupportTicket.objects.select_related("requester", "assigned_to").prefetch_related("comments")
        if self.request.user.is_staff:
            return qs
        return qs.exclude(requester=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=["delete"])
    def comment(self, request, pk=None):
        ticket = self.get_object()
        serializer = SupportTicketCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = wrap_service(
            add_ticket_comment,
            ticket,
            request.user,
            serializer.validated_data["body"],
            serializer.validated_data.get("internal", False),
        )
        return Response(SupportTicketCommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        ticket = wrap_service(resolve_ticket, self.get_object(), request.user, request.data.get("resolution", "Resolved"))
        return Response(self.get_serializer(ticket).data)


class ModerationCaseViewSet(viewsets.ModelViewSet):
    queryset = ModerationCase.objects.all()
    serializer_class = ModerationCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def decide(self, request, pk=None):
        case = wrap_service(
            decide_moderation_case,
            self.get_object(),
            decision=request.data.get("decision", ""),
            status=request.data.get("status", ModerationCase.Status.ACTIONED),
        )
        return Response(self.get_serializer(case).data)


class DataExportJobViewSet(viewsets.ModelViewSet):
    serializer_class = DataExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = DataExportJob.objects.all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(requested_by=self.request.user)

    def create(self, request, *args, **kwargs):
        job = wrap_service(queue_export, request.user, request.data.get("export_type", "generic"), request.data.get("filters", {}))
        return Response(self.get_serializer(job).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def export(self, request):
        job = wrap_service(queue_export, request.user, request.data.get("export_type", "generic"), request.data.get("filters", {}))
        return Response(self.get_serializer(job).data, status=status.HTTP_201_CREATED)


class SystemAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = SystemAnnouncement.objects.all()
    serializer_class = SystemAnnouncementSerializer
    permission_classes = [StaffWritePermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PlatformBootstrapView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(bootstrap_payload(request.user))
