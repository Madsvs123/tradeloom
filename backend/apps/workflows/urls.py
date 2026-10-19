from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    EscalationRuleViewSet,
    InboxView,
    WorkflowDefinitionViewSet,
    WorkflowInstanceViewSet,
    WorkflowTaskViewSet,
    WorkflowTransitionViewSet,
)

app_name = "workflows"

router = DefaultRouter()
router.register("definitions", WorkflowDefinitionViewSet, basename="workflows-definitions")
router.register("instances", WorkflowInstanceViewSet, basename="workflows-instances")
router.register("workflow-tasks", WorkflowTaskViewSet, basename="workflows-tasks")
router.register("transitions", WorkflowTransitionViewSet, basename="workflows-transitions")
router.register("escalation-rules", EscalationRuleViewSet, basename="workflows-escalation-rules")

urlpatterns = [
    path("inbox/", InboxView.as_view(), name="inbox"),
    path("", include(router.urls)),
]
