from rest_framework import serializers

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


class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = "__all__"
        read_only_fields = ("id", "status", "progress_percent", "created_at", "updated_at")


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = "__all__"
        read_only_fields = ("id", "status", "achieved_at", "created_at", "updated_at")


class ProjectDeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDeliverable
        fields = "__all__"
        read_only_fields = ("id", "status", "submitted_at", "submitted_by", "approved_by", "approved_at", "created_at", "updated_at")


class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTask
        fields = "__all__"
        read_only_fields = ("id", "status", "completed_at", "created_at", "updated_at")


class ProjectBudgetLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBudgetLine
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ProjectVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectVendor
        fields = "__all__"
        read_only_fields = ("id", "status", "assigned_at", "removed_at", "created_at", "updated_at")


class ProjectRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRisk
        fields = "__all__"
        read_only_fields = ("id", "score", "created_by", "created_at", "updated_at")


class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        fields = "__all__"
        read_only_fields = ("id", "uploaded_by", "created_at", "updated_at")


class ProjectSerializer(serializers.ModelSerializer):
    phases = ProjectPhaseSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    budget_lines = ProjectBudgetLineSerializer(many=True, read_only=True)
    vendor_count = serializers.IntegerField(source="vendors.count", read_only=True)
    task_count = serializers.IntegerField(source="tasks.count", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("id", "reference", "owner", "status", "progress_percent", "started_at", "completed_at", "created_at", "updated_at")
