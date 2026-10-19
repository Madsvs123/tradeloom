import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(blank=True, max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("on_hold", "On Hold"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=16,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "progress_percent",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="procurement_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="ProjectPhase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("on_hold", "On Hold"),
                        ],
                        default="not_started",
                        max_length=16,
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "progress_percent",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="phases",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ("project", "order", "id"),
                "unique_together": {("project", "order")},
            },
        ),
        migrations.CreateModel(
            name="ProjectMilestone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("achieved", "Achieved"),
                            ("missed", "Missed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                ("achieved_at", models.DateTimeField(blank=True, null=True)),
                ("achievement_notes", models.TextField(blank=True)),
                (
                    "phase",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="milestones",
                        to="projects.projectphase",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="milestones",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ("due_date", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProjectDeliverable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("in_progress", "In Progress"),
                            ("submitted", "Submitted"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="not_started",
                        max_length=16,
                    ),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("file_url", models.URLField(blank=True)),
                ("review_notes", models.TextField(blank=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="project_deliverables_approved",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "milestone",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="deliverables",
                        to="projects.projectmilestone",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deliverables",
                        to="projects.project",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="project_deliverables_submitted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("due_date", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProjectTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("todo", "To Do"),
                            ("in_progress", "In Progress"),
                            ("done", "Done"),
                            ("blocked", "Blocked"),
                        ],
                        default="todo",
                        max_length=16,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        max_length=8,
                    ),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "estimated_hours",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=8,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "actual_hours",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=8,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="project_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "phase",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tasks",
                        to="projects.projectphase",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ("project", "due_date", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProjectBudgetLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=255)),
                (
                    "planned_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "committed_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "spent_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "Planned"),
                            ("committed", "Committed"),
                            ("spent", "Spent"),
                            ("closed", "Closed"),
                        ],
                        default="planned",
                        max_length=12,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="budget_lines",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ("project", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProjectVendor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("role", models.CharField(blank=True, max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("invited", "Invited"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("removed", "Removed"),
                        ],
                        default="invited",
                        max_length=12,
                    ),
                ),
                ("assigned_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("removed_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vendors",
                        to="projects.project",
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="project_vendor_roles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("project", "id"),
                "unique_together": {("project", "vendor")},
            },
        ),
        migrations.CreateModel(
            name="ProjectRisk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("schedule", "Schedule"),
                            ("cost", "Cost"),
                            ("quality", "Quality"),
                            ("supply", "Supply"),
                            ("legal", "Legal"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=16,
                    ),
                ),
                ("likelihood", models.PositiveSmallIntegerField(default=1)),
                ("impact", models.PositiveSmallIntegerField(default=1)),
                ("score", models.PositiveSmallIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("identified", "Identified"),
                            ("mitigating", "Mitigating"),
                            ("occurred", "Occurred"),
                            ("resolved", "Resolved"),
                        ],
                        default="identified",
                        max_length=16,
                    ),
                ),
                ("mitigation_plan", models.TextField(blank=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="project_risks_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="project_risks_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="risks",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "ordering": ("-score", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProjectDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("contract", "Contract"),
                            ("specification", "Specification"),
                            ("report", "Report"),
                            ("approval", "Approval"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=16,
                    ),
                ),
                ("file_name", models.CharField(max_length=255)),
                ("file_url", models.URLField()),
                ("content_type", models.CharField(blank=True, max_length=120)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="projects.project",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="project_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("project", "id"),
            },
        ),
    ]
