from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PlatformSetting(TimeStampedModel):
    key = models.CharField(max_length=120, unique=True)
    value = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.key


class FeatureFlag(TimeStampedModel):
    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    audience = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return f"{self.key} ({'on' if self.enabled else 'off'})"


class BillingPlan(TimeStampedModel):
    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    name = models.CharField(max_length=160)
    code = models.CharField(max_length=40, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    billing_cycle = models.CharField(max_length=16, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("price",)

    def __str__(self):
        return f"{self.name} ({self.currency} {self.price}/{self.billing_cycle})"


class TenantSubscription(TimeStampedModel):
    class Status(models.TextChoices):
        TRIAL = "trial", "Trial"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        CANCELLED = "cancelled", "Cancelled"

    tenant_name = models.CharField(max_length=160)
    plan = models.ForeignKey(BillingPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TRIAL)
    started_at = models.DateTimeField(default=timezone.now)
    renews_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("tenant_name", "plan")

    def __str__(self):
        return f"{self.tenant_name} — {self.plan.code} ({self.status})"


class UsageQuota(TimeStampedModel):
    plan = models.ForeignKey(BillingPlan, on_delete=models.CASCADE, related_name="usage_quotas")
    resource_key = models.CharField(max_length=80)
    limit = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=40, default="units")

    class Meta:
        ordering = ("plan", "resource_key")
        unique_together = ("plan", "resource_key")

    def __str__(self):
        return f"{self.plan.code}.{self.resource_key} = {self.limit}"


class TenantHealth(TimeStampedModel):
    class Status(models.TextChoices):
        OK = "ok", "OK"
        DEGRADED = "degraded", "Degraded"
        DOWN = "down", "Down"

    tenant_name = models.CharField(max_length=160)
    component = models.CharField(max_length=120, default="core")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OK)
    last_checked_at = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-last_checked_at",)

    def __str__(self):
        return f"{self.tenant_name}/{self.component} {self.status}"


class MaintenanceWindow(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="maintenance_windows"
    )

    class Meta:
        ordering = ("-starts_at",)

    def __str__(self):
        return self.title


class RbacPolicy(TimeStampedModel):
    class Permission(models.TextChoices):
        VIEW = "view", "View"
        EDIT = "edit", "Edit"
        CREATE = "create", "Create"
        DELETE = "delete", "Delete"
        APPROVE = "approve", "Approve"

    role = models.CharField(max_length=80)
    resource = models.CharField(max_length=120)
    permission = models.CharField(max_length=16, choices=Permission.choices)
    is_allowed = models.BooleanField(default=True)
    scope = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("role", "resource", "permission")
        unique_together = ("role", "resource", "permission")

    def __str__(self):
        return f"{self.role} {self.permission} {self.resource}"


class OperationalSla(TimeStampedModel):
    module = models.CharField(max_length=80)
    name = models.CharField(max_length=160)
    target_hours = models.PositiveIntegerField(default=24)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("module", "name")


class SupportTicket(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets"
    )
    subject = models.CharField(max_length=180)
    body = models.TextField()
    module = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.NORMAL)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.subject


class SupportTicketComment(TimeStampedModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_comments")
    body = models.TextField()
    internal = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)


class ModerationCase(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACTIONED = "actioned", "Actioned"
        DISMISSED = "dismissed", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderation_reports"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderation_cases"
    )
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=64)
    reason = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    decision = models.CharField(max_length=80, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class DataExportJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="export_jobs")
    export_type = models.CharField(max_length=80)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    file_url = models.URLField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class SystemAnnouncement(TimeStampedModel):
    title = models.CharField(max_length=180)
    body = models.TextField()
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("-starts_at",)

    def __str__(self):
        return self.title
