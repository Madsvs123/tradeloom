from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import (
    Project,
    ProjectBudgetLine,
    ProjectDeliverable,
    ProjectDocument,
    ProjectMilestone,
    ProjectPhase,
    ProjectRisk,
    ProjectTask,
    ProjectVendor,
)
from .serializers import (
    ProjectBudgetLineSerializer,
    ProjectDeliverableSerializer,
    ProjectDocumentSerializer,
    ProjectMilestoneSerializer,
    ProjectPhaseSerializer,
    ProjectRiskSerializer,
    ProjectSerializer,
    ProjectTaskSerializer,
    ProjectVendorSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


class ProjectViewSet(AuthenticatedViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.prefetch_related("phases", "milestones", "budget_lines", "vendors", "tasks")
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user) | qs.filter(vendors__vendor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        project = wrap_service(services.start_project, self.get_object(), actor=request.user)
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        project = wrap_service(services.complete_project, self.get_object(), actor=request.user)
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"], url_path="update-progress")
    def update_progress(self, request, pk=None):
        project = self.get_object()
        progress = request.data.get("progress_percent")
        if progress is not None:
            value = Decimal(str(progress))
            if value < 0 or value > 100:
                raise ValidationError("progress_percent must be between 0 and 100.")
            project.progress_percent = value
            project.save(update_fields=["progress_percent", "updated_at"])
        else:
            project = wrap_service(services.update_project_progress, project)
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"], url_path="add-risk")
    def add_risk(self, request, pk=None):
        risk = wrap_service(
            services.add_risk,
            self.get_object(),
            request.user,
            request.data.get("title", ""),
            likelihood=request.data.get("likelihood", 1),
            impact=request.data.get("impact", 1),
            description=request.data.get("description", ""),
            category=request.data.get("category", ProjectRisk.Category.OTHER),
            owner=request.data.get("owner"),
            mitigation_plan=request.data.get("mitigation_plan", ""),
            due_date=request.data.get("due_date"),
        )
        return Response(ProjectRiskSerializer(risk).data, status=status.HTTP_201_CREATED)


class ProjectPhaseViewSet(AuthenticatedViewSet):
    serializer_class = ProjectPhaseSerializer

    def get_queryset(self):
        qs = ProjectPhase.objects.select_related("project")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user) | qs.filter(
            project__vendors__vendor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        phase = wrap_service(services.complete_phase, self.get_object(), actor=request.user)
        return Response(self.get_serializer(phase).data)


class ProjectMilestoneViewSet(AuthenticatedViewSet):
    serializer_class = ProjectMilestoneSerializer

    def get_queryset(self):
        qs = ProjectMilestone.objects.select_related("project", "phase")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user) | qs.filter(
            project__vendors__vendor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def achieve(self, request, pk=None):
        milestone = wrap_service(
            services.achieve_milestone,
            self.get_object(),
            actor=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(milestone).data)


class ProjectDeliverableViewSet(AuthenticatedViewSet):
    serializer_class = ProjectDeliverableSerializer

    def get_queryset(self):
        qs = ProjectDeliverable.objects.select_related("project", "milestone", "submitted_by", "approved_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user) | qs.filter(
            project__vendors__vendor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        deliverable = wrap_service(
            services.submit_deliverable,
            self.get_object(),
            request.user,
            file_url=request.data.get("file_url", ""),
            notes=request.data.get("notes", ""),
        )
        return Response(self.get_serializer(deliverable).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        deliverable = wrap_service(
            services.review_deliverable,
            self.get_object(),
            request.user,
            True,
            review_notes=request.data.get("review_notes", ""),
        )
        return Response(self.get_serializer(deliverable).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        deliverable = wrap_service(
            services.review_deliverable,
            self.get_object(),
            request.user,
            False,
            review_notes=request.data.get("review_notes", ""),
        )
        return Response(self.get_serializer(deliverable).data)


class ProjectTaskViewSet(AuthenticatedViewSet):
    serializer_class = ProjectTaskSerializer

    def get_queryset(self):
        qs = ProjectTask.objects.select_related("project", "phase", "assignee")
        if self.request.user.is_staff:
            return qs
        return qs.filter(assignee=self.request.user) | qs.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = wrap_service(
            services.complete_task,
            self.get_object(),
            actor=request.user,
            actual_hours=request.data.get("actual_hours"),
        )
        return Response(self.get_serializer(task).data)


class ProjectBudgetLineViewSet(AuthenticatedViewSet):
    serializer_class = ProjectBudgetLineSerializer

    def get_queryset(self):
        qs = ProjectBudgetLine.objects.select_related("project")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user)


class ProjectVendorViewSet(AuthenticatedViewSet):
    serializer_class = ProjectVendorSerializer

    def get_queryset(self):
        qs = ProjectVendor.objects.select_related("project", "vendor")
        if self.request.user.is_staff:
            return qs
        return qs.filter(vendor=self.request.user) | qs.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class ProjectRiskViewSet(AuthenticatedViewSet):
    serializer_class = ProjectRiskSerializer

    def get_queryset(self):
        qs = ProjectRisk.objects.select_related("project", "owner", "created_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user) | qs.filter(
            project__vendors__vendor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def mitigate(self, request, pk=None):
        risk = wrap_service(
            services.record_risk_status,
            self.get_object(),
            ProjectRisk.Status.MITIGATING,
            actor=request.user,
        )
        return Response(self.get_serializer(risk).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        risk = wrap_service(
            services.record_risk_status,
            self.get_object(),
            ProjectRisk.Status.RESOLVED,
            actor=request.user,
        )
        return Response(self.get_serializer(risk).data)


class ProjectDocumentViewSet(AuthenticatedViewSet):
    serializer_class = ProjectDocumentSerializer

    def get_queryset(self):
        qs = ProjectDocument.objects.select_related("project", "uploaded_by")
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user) | qs.filter(
            project__vendors__vendor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
