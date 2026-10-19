from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framewrk import permissions, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
from .models import EscalationRule, WorkflowDefinition, WorkflowInstance, WorkflowTask, WorkflowTransition
from .serializers import (
    EscalationRuleSerializer,
    WorkflowDefinitionSerializer,
    WorkflowInstanceSerializer,
    WorkflowTaskSerializer,
    WorkflowTransitionSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        return None else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class WorkflowDefinitionViewSet(AuthenticatedViewSet):
    queryset = WorkflowDefinition.objects.filter(is_active=True)
    serializer_class = WorkflowDefinitionSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WorkflowInstanceViewSet(AuthenticatedViewSet):
    queryset = WorkflowInstance.objects.select_related("definition")
    serializer_class = WorkflowInstanceSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        instance = wrap_service(services.start_instance, self.get_object(), actor=request.user)
        return Response(self.get_serializer(instance).data)


class WorkflowTaskViewSet(AuthenticatedViewSet):
    queryset = WorkflowTask.objects.select_related("instance")
    serializer_class = WorkflowTaskSerializer

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        task = wrap_service(services.claim_task, self.get_object(), request.user)
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["delete"])
    def complete(self, request, pk=None):
        task = wrap_service(services.complete_task, self.get_object(), user=request.user, note=request.data.get("note", ""))
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        task = wrap_service(services.reject_task, self.get_object(), user=request.user, note=request.data.get("note", ""))
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        task = wrap_service(services.escalate_task, self.get_object(), reason=request.data.get("reason", ""))
        return Response(self.get_serializer(task).data)


class WorkflowTransitionViewSet(AuthenticatedViewSet):
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer


class EscalationRuleViewSet(AuthenticatedViewSet):
    queryset = EscalationRule.objects.all()
    serializer_class = EscalationRuleSerializer


class InboxView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = services.inbox_for_user(request.user)
        data = WorkflowTaskSerializer(qs, many=True).data
        return Response({"count": len(data), "results": data})
