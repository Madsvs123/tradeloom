from django.contrib import admin

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


class ProjectPhaseInline(admin.TabularInline):
    model = ProjectPhase
    extra = 0


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0


class ProjectDeliverableInline(admin.TabularInline):
    model = ProjectDeliverable
    extra = 0


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0


class ProjectBudgetLineInline(admin.TabularInline):
    model = ProjectBudgetLine
    extra = 0


class ProjectVendorInline(admin.TabularInline):
    model = ProjectVendor
    extra = 0


class ProjectRiskInline(admin.TabularInline):
    model = ProjectRisk
    extra = 0


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "owner", "status", "category", "progress_percent", "start_date", "end_date")
    list_filter = ("status", "category")
    search_fields = ("reference", "title")
    inlines = (
        ProjectPhaseInline,
        ProjectMilestoneInline,
        ProjectDeliverableInline,
        ProjectTaskInline,
        ProjectBudgetLineInline,
        ProjectVendorInline,
        ProjectRiskInline,
        ProjectDocumentInline,
    )


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ("project", "name", "order", "status", "progress_percent", "start_date", "end_date")
    list_filter = ("status",)


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "phase", "status", "due_date", "achieved_at")
    list_filter = ("status",)


@admin.register(ProjectDeliverable)
class ProjectDeliverableAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "milestone", "status", "due_date", "submitted_at")
    list_filter = ("status",)


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "assignee", "status", "priority", "due_date")
    list_filter = ("status", "priority")


@admin.register(ProjectBudgetLine)
class ProjectBudgetLineAdmin(admin.ModelAdmin):
    list_display = ("project", "category", "planned_amount", "committed_amount", "spent_amount", "status")
    list_filter = ("status", "category")


@admin.register(ProjectVendor)
class ProjectVendorAdmin(admin.ModelAdmin):
    list_display = ("project", "vendor", "role", "status", "assigned_at")
    list_filter = ("status",)


@admin.register(ProjectRisk)
class ProjectRiskAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "category", "likelihood", "impact", "score", "status", "owner")
    list_filter = ("status", "category")


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "project", "category", "uploaded_by")
    list_filter = ("category",)
