from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectBudgetLineViewSet,
    ProjectDeliverableViewSet,
    ProjectDocumentViewSet,
    ProjectMilestoneViewSet,
    ProjectPhaseViewSet,
    ProjectRiskViewSet,
    ProjectTaskViewSet,
    ProjectVendorViewSet,
    ProjectViewSet,
)

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("project-phases", ProjectPhaseViewSet, basename="project-phase")
router.register("project-milestones", ProjectMilestoneViewSet, basename="project-milestone")
router.register("project-deliverables", ProjectDeliverableViewSet, basename="project-deliverable")
router.register("project-tasks", ProjectTaskViewSet, basename="project-task")
router.register("project-budget-lines", ProjectBudgetLineViewSet, basename="project-budget-line")
router.register("project-vendors", ProjectVendorViewSet, basename="project-vendor")
router.register("project-risks", ProjectRiskViewSet, basename="project-risk")
router.register("project-documents", ProjectDocumentViewSet, basename="project-document")

urlpatterns = [
    path("", include(router.urls)),
]
