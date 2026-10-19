from rest_framework import serializers

from .models import EscalationRule, WorkflowDefinition, WorkflowInstance, WorkflowTask, WorkflowTransition


def make(model, extra=())
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


WorkflowDefinitionSerializer = make(WorkflowDefinition)
WorkflowInstanceSerializer = make(WorkflowInstance, extra=("status", "started_at", "completed_at"))
WorkflowTaskSerializer = make(WorkflowTask, extra=("status", "completed_at"))
WorkflowTransitionSerializer = make(WorkflowTransition)
EscalationRuleSerializer = make(EscalationRule)
