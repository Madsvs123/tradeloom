from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Project,
    ProjectDeliverable,
    ProjectMilestone,
    ProjectPhase,
    ProjectRisk,
    ProjectTask,
)

PROJECT_TRANSITIONS = {
    Project.Status.DRAFT: {Project.Status.ACTIVE, Project.Status.CANCELLED},
    Project.Status.ACTIVE: {Project.Status.ON_HOLD, Project.Status.COMPLETED, Project.Status.CANCELLED},
    Project.Status.ON_HOLD: {Project.Status.ACTIVE, Project.Status.COMPLETED, Project.Status.CANCELLED},
    Project.Status.COMPLETED: set(),
    Project.Status.CANCELLED: set(),
}

PHASE_TRANSITIONS = {
    ProjectPhase.Status.NOT_STARTED: {ProjectPhase.Status.IN_PROGRESS, ProjectPhase.Status.ON_HOLD},
    ProjectPhase.Status.IN_PROGRESS: {ProjectPhase.Status.COMPLETED, ProjectPhase.Status.ON_HOLD},
    ProjectPhase.Status.ON_HOLD: {ProjectPhase.Status.IN_PROGRESS, ProjectPhase.Status.COMPLETED},
    ProjectPhase.Status.COMPLETED: set(),
}

MILESTONE_TRANSITIONS = {
    ProjectMilestone.Status.PENDING: {ProjectMilestone.Status.IN_PROGRESS, ProjectMilestone.Status.MISSED},
    ProjectMilestone.Status.IN_PROGRESS: {ProjectMilestone.Status.ACHIEVED, ProjectMilestone.Status.MISSED},
    ProjectMilestone.Status.ACHIEVED: set(),
    ProjectMilestone.Status.MISSED: set(),
}

DELIVERABLE_TRANSITIONS = {
    ProjectDeliverable.Status.NOT_STARTED: {ProjectDeliverable.Status.IN_PROGRESS, ProjectDeliverable.Status.SUBMITTED},
    ProjectDeliverable.Status.IN_PROGRESS: {ProjectDeliverable.Status.SUBMITTED, ProjectDeliverable.Status.REJECTED},
    ProjectDeliverable.Status.SUBMITTED: {ProjectDeliverable.Status.APPROVED, ProjectDeliverable.Status.REJECTED},
    ProjectDeliverable.Status.APPROVED: set(),
    ProjectDeliverable.Status.REJECTED: {ProjectDeliverable.Status.IN_PROGRESS, ProjectDeliverable.Status.SUBMITTED},
}

RISK_TRANSITIONS = {
    ProjectRisk.Status.IDENTIFIED: {ProjectRisk.Status.MITIGATING, ProjectRisk.Status.OCCURRED, ProjectRisk.Status.RESOLVED},
    ProjectRisk.Status.MITIGATING: {ProjectRisk.Status.OCCURRED, ProjectRisk.Status.RESOLVED},
    ProjectRisk.Status.OCCURRED: {ProjectRisk.Status.RESOLVED},
    ProjectRisk.Status.RESOLVED: set(),
}


def update_project_progress(project):
    phases = project.phases.all()
    if phases.exists():
        total = sum((phase.progress_percent for phase in phases), Decimal("0.00"))
        progress = (total / Decimal(len(phases))).quantize(Decimal("0.01"))
    else:
        progress = project.progress_percent
    project.progress_percent = progress
    project.save(update_fields=["progress_percent", "updated_at"])
    return project


def start_project(project, actor=None):
    allowed = PROJECT_TRANSITIONS.get(project.status, set())
    if Project.Status.ACTIVE not in allowed:
        raise ValidationError(f"Cannot start a project in status '{project.status}'.")
    if not project.start_date or not project.end_date:
        raise ValidationError("Set both start_date and end_date before starting the project.")
    if project.end_date < project.start_date:
        raise ValidationError("The project end date cannot be before its start date.")
    project.status = Project.Status.ACTIVE
    project.started_at = timezone.now()
    project.save(update_fields=["status", "started_at", "updated_at"])
    return project


def complete_project(project, actor=None):
    allowed = PROJECT_TRANSITIONS.get(project.status, set())
    if Project.Status.COMPLETED not in allowed:
        raise ValidationError("Only active or on-hold projects can be completed.")
    update_project_progress(project)
    if project.progress_percent < Decimal("100.00"):
        raise ValidationError("All phases must reach 100% before the project can be completed.")
    project.status = Project.Status.COMPLETED
    project.completed_at = timezone.now()
    project.save(update_fields=["status", "completed_at", "updated_at"])
    return project


@transaction.atomic
def complete_phase(phase, actor=None):
    allowed = PHASE_TRANSITIONS.get(phase.status, set())
    if ProjectPhase.Status.COMPLETED not in allowed:
        raise ValidationError("Only in-progress phases can be completed.")
    open_tasks = phase.project.tasks.all().exclude(status=ProjectTask.Status.DONE)
    if open_tasks.exists():
        raise ValidationError("Complete or close all tasks in the phase before completing it.")
    phase.status = ProjectPhase.Status.COMPLETED
    phase.progress_percent = Decimal("100.00")
    phase.save(update_fields=["status", "progress_percent", "updated_at"])
    update_project_progress(phase.project)
    return phase


def achieve_milestone(milestone, actor=None, notes=""):
    allowed = MILESTONE_TRANSITIONS.get(milestone.status, set())
    if ProjectMilestone.Status.ACHIEVED not in allowed:
        raise ValidationError("Only pending or in-progress milestones can be achieved.")
    milestone.status = ProjectMilestone.Status.ACHIEVED
    milestone.achieved_at = timezone.now()
    milestone.achievement_notes = notes
    milestone.save(update_fields=["status", "achieved_at", "achievement_notes", "updated_at"])
    return milestone


@transaction.atomic
def submit_deliverable(deliverable, actor, file_url="", notes=""):
    allowed = DELIVERABLE_TRANSITIONS.get(deliverable.status, set())
    if ProjectDeliverable.Status.SUBMITTED not in allowed:
        raise ValidationError(f"Cannot submit a deliverable in status '{deliverable.status}'.")
    if not file_url:
        raise ValidationError("A file_url is required when submitting a deliverable.")
    deliverable.status = ProjectDeliverable.Status.SUBMITTED
    deliverable.submitted_at = timezone.now()
    deliverable.submitted_by = actor
    deliverable.file_url = file_url
    deliverable.review_notes = notes or deliverable.review_notes
    deliverable.save(
        update_fields=["status", "submitted_at", "submitted_by", "file_url", "review_notes", "updated_at"]
    )
    milestone = deliverable.milestone
    if milestone and milestone.status == ProjectMilestone.Status.PENDING:
        milestone.status = ProjectMilestone.Status.IN_PROGRESS
        milestone.save(update_fields=["status", "updated_at"])
    return deliverable


def review_deliverable(deliverable, actor, approved, review_notes=""):
    to_status = (
        ProjectDeliverable.Status.APPROVED if approved else ProjectDeliverable.Status.REJECTED
    )
    allowed = DELIVERABLE_TRANSITIONS.get(deliverable.status, set())
    if to_status not in allowed:
        raise ValidationError("Only submitted deliverables can be reviewed.")
    deliverable.status = to_status
    deliverable.approved_by = actor
    deliverable.approved_at = timezone.now() if approved else deliverable.approved_at
    deliverable.review_notes = review_notes
    deliverable.save(
        update_fields=["status", "approved_by", "approved_at", "review_notes", "updated_at"]
    )
    return deliverable


def add_risk(project, created_by, title, likelihood=1, impact=1, description="", category=ProjectRisk.Category.OTHER, owner=None, mitigation_plan="", due_date=None):
    if not title or not title.strip():
        raise ValidationError("A risk title is required.")
    try:
        likelihood = int(likelihood)
        impact = int(impact)
    except (TypeError, ValueError):
        raise ValidationError("Likelihood and impact must be whole numbers between 1 and 5.")
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        raise ValidationError("Likelihood and impact must be between 1 and 5.")
    risk = ProjectRisk.objects.create(
        project=project,
        created_by=created_by,
        title=title,
        description=description,
        category=category,
        likelihood=likelihood,
        impact=impact,
        owner=owner,
        mitigation_plan=mitigation_plan,
        due_date=due_date,
    )
    return risk


def record_risk_status(risk, to_status, actor=None):
    allowed = RISK_TRANSITIONS.get(risk.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move risk from '{risk.status}' to '{to_status}'.")
    risk.status = to_status
    risk.save(update_fields=["status", "updated_at"])
    return risk


def complete_task(task, actor=None, actual_hours=None):
    if task.status != ProjectTask.Status.DONE:
        raise ValidationError("This task is already done.")
    if actual_hours is not None:
        task.actual_hours = actual_hours
    task.status = ProjectTask.Status.DONE
    task.completed_at = timezone.now()
    task.save(update_fields=["status", "actual_hours", "completed_at", "updated_at"])
    return task
