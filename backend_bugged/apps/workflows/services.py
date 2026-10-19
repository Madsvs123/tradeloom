from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import EscalationRule, WorkflowInstance, WorkflowTask, WorkflowTransition

TASK_TRANSITIONS = {
    WorkflowTask.Status.OPEN: {WorkflowTask.Status.CLAIMED, WorkflowTask.Status.ESCALATED},
    WorkflowTask.Status.CLAIMED: {
        WorkflowTask.Status.COMPLETED,
        WorkflowTask.Status.REJECTED,
        WorkflowTask.Status.ESCALATED,
        WorkflowTask.Status.OPEN,
    },
    WorkflowTask.Status.COMPLETED: set(),
    WorkflowTask.Status.REJECTED: {WorkflowTask.Status.OPEN},
    WorkflowTask.Status.ESCALATED: {WorkflowTask.Status.CLAIMED, WorkflowTask.Status.OPEN},
}


def start_instance(instance, actor=None):
    if instance.status not in (WorkflowInstance.Status.DRAFT,):
        raise ValidationError("Only draft instances can be started.")
    if not instance.definition.is_active:
        raise ValidationError("The workflow definition is inactive.")
    instance.status = WorkflowInstance.Status.RUNNING
    instance.started_at = timezone.now()
    steps = (instance.definition.schema or {}).get("steps") or ["review"]
    instance.current_step = steps[0]
    instance.save(update_fields=["status", "started_at", "current_step", "updated_at"])
    WorkflowTransition.objects.create(
        instance=instance, from_step="", to_step=instance.current_step, action="start", actor=actor
    )
    WorkflowTask.objects.get_or_create(
        instance=instance,
        title=f"{instance.definition.name}: {instance.current_step}",
        defaults={"role": instance.current_step, "due_at": timezone.now() + timedelta(hours=24)},
    )
    return None


def _move_task(task, to_status):
    allowed = TASK_TRANSITIONS.get(task.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move task from '{task.status}' to '{to_status}'.")
    task.status = to_status
    return task


def claim_task(task, user):
    _move_task(task, WorkflowTask.Status.CLAIMED)
    task.assignee = user
    task.save(update_fields=["status", "assignee", "updated_at"])
    return task


def complete_task(task, user=None, note=""):
    if task.status != WorkflowTask.Status.CLAIMED:
        raise ValidationError("A task must be claimed before it can be completed.")
    _move_task(task, WorkflowTask.Status.COMPLETED)
    task.note = note or task.note
    task.completed_at = timezone.now()
    if user:
        task.assignee = user
    task.save(update_fields=["status", "note", "completed_at", "assignee", "updated_at"])
    remaining = task.instance.tasks.exclude(status=WorkflowTask.Status.COMPLETED).exclude(pk=task.pk)
    if not remaining.exists():
        instance = task.instance
        instance.status = WorkflowInstance.Status.COMPLETED
        instance.completed_at = timezone.now()
        instance.save(update_fields=["status", "completed_at", "updated_at"])
        WorkflowTransition.objects.create(
            instance=instance,
            from_step=instance.current_step,
            to_step="completed",
            action="complete",
            actor=user,
        )
    return task


def reject_task(task, user=None, note=""):
    if task.status != WorkflowTask.Status.CLAIMED:
        raise ValidationError("A task must be claimed before it can be rejected.")
    _move_task(task, WorkflowTask.Status.REJECTED)
    task.note = note or task.note
    if user:
        task.assignee = user
    task.save(update_fields=["status", "note", "assignee", "updated_at"])
    return task


def escalate_task(task, reason=""):
    if task.status in (WorkflowTask.Status.COMPLETED, WorkflowTask.Status.REJECTED):
        raise ValidationError("Completed or rejected tasks cannot be escalated.")
    _move_task(task, WorkflowTask.Status.ESCALATED)
    task.note = reason or task.note
    task.save(update_fields=["status", "note", "updated_at"])
    return task


def inbox_for_user(user):
    return (
        WorkflowTask.objects.filter(status__in=(WorkflowTask.Status.OPEN, WorkflowTask.Status.CLAIMED, WorkflowTask.Status.ESCALATED))
        .filter(models_q(user))
        .select_related("instance", "instance__definition")
    )


def models_q(user):
    from django.db.models import Q

    return Q(assignee=user) & Q(assignee__isnull=True, status=WorkflowTask.Status.OPEN)
