import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Project(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="procurement_projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default="USD")
    progress_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PRJ-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class ProjectPhase(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="phases")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NOT_STARTED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    progress_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ("project", "order", "id")
        unique_together = ("project", "order")

    def __str__(self):
        return f"{self.project.reference} - {self.name}"


class ProjectMilestone(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        ACHIEVED = "achieved", "Achieved"
        MISSED = "missed", "Missed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    phase = models.ForeignKey(
        ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True, related_name="milestones"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    achieved_at = models.DateTimeField(null=True, blank=True)
    achievement_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("due_date", "id")

    def __str__(self):
        return f"{self.project.reference} - {self.title}"


class ProjectDeliverable(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliverables")
    milestone = models.ForeignKey(
        ProjectMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliverables"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NOT_STARTED)
    due_date = models.DateField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_deliverables_submitted",
    )
    file_url = models.URLField(blank=True)
    review_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_deliverables_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("due_date", "id")

    def __str__(self):
        return f"{self.project.reference} - {self.title}"


class ProjectTask(TimeStampedModel):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        BLOCKED = "blocked", "Blocked"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    phase = models.ForeignKey(
        ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("project", "due_date", "id")

    def __str__(self):
        return f"{self.project.reference} - {self.title}"


class ProjectBudgetLine(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        COMMITTED = "committed", "Committed"
        SPENT = "spent", "Spent"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="budget_lines")
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    planned_amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    committed_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    spent_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PLANNED)

    class Meta:
        ordering = ("project", "id")

    def __str__(self):
        return f"{self.project.reference} - {self.category}"


class ProjectVendor(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        REMOVED = "removed", "Removed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="vendors")
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="project_vendor_roles")
    role = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.INVITED)
    assigned_at = models.DateTimeField(default=timezone.now)
    removed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("project", "id")
        unique_together = ("project", "vendor")

    def __str__(self):
        return f"{self.project.reference} - {self.vendor}"


class ProjectRisk(TimeStampedModel):
    class Category(models.TextChoices):
        SCHEDULE = "schedule", "Schedule"
        COST = "cost", "Cost"
        QUALITY = "quality", "Quality"
        SUPPLY = "supply", "Supply"
        LEGAL = "legal", "Legal"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        IDENTIFIED = "identified", "Identified"
        MITIGATING = "mitigating", "Mitigating"
        OCCURRED = "occurred", "Occurred"
        RESOLVED = "resolved", "Resolved"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="risks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=16, choices=Category.choices, default=Category.OTHER)
    likelihood = models.PositiveSmallIntegerField(default=1)
    impact = models.PositiveSmallIntegerField(default=1)
    score = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.IDENTIFIED)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_risks_owned",
    )
    mitigation_plan = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="project_risks_created"
    )

    class Meta:
        ordering = ("-score", "id")

    def __str__(self):
        return f"{self.project.reference} - {self.title}"

    def save(self, *args, **kwargs):
        self.score = self.likelihood + self.impact
        super().save(*args, **kwargs)


class ProjectDocument(TimeStampedModel):
    class Category(models.TextChoices):
        CONTRACT = "contract", "Contract"
        SPECIFICATION = "specification", "Specification"
        REPORT = "report", "Report"
        APPROVAL = "approval", "Approval"
        OTHER = "other", "Other"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="project_documents"
    )
    category = models.CharField(max_length=16, choices=Category.choices, default=Category.OTHER)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    content_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ("project", "id")

    def __str__(self):
        return self.file_name
