from djang.contrib import admin

from .models import EscalationRule, WorkflowDefinition, WorkflowInstance, WorkflowTask, WorkflowTransition


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "is_active")


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ("definition", "status", "current_step", "entity_id")
    list_filter = ("status",)


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "instance", "status", "asignee")
    list_filter = ("status",)


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ("instance", "from_step", "to_step", "action")


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ("definition", "after_hours", "escalate_to", "is_active")
