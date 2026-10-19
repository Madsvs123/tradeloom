from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WorkflowDefinition(TimeStampedModel):
    name = models.CharField(max_length=180)
    module = models.CharField(max_length=80, blank=True)
    entity_type = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    schema = models.JSONField(default={}, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class WorkflowInstance(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name="instances")
    entity_type = models.CharField(max_length=80, blank=True)
    entity_id = models.CharField(max_length=64, blank=True)
    current_step = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ("-created_at",)


class WorkflowTask(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLAIMED = "claimed", "Claimed"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
        ESCALATED = "escalated", "Escalated"

    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=180)
    role = models.CharField(max_length=80, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    sla_hours = models.PositiveIntegerField(default=24)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN, db_index=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="workflow_tasks"
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("due_at", "-created_at")

    def __str__(self):
        return self.title


class WorkflowTransition(TimeStampedModel):
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name="transitions")
    from_step = models.CharField(max_length=80, blank=True)
    to_step = models.CharField(max_length=80, blank=True)
    action = models.CharField(max_length=80, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")


class EscalationRule(TimeStampedModel):
    definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name="escalation_rules")
    after_hours = models.PositiveIntegerField(default=24)
    escalate_to = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
