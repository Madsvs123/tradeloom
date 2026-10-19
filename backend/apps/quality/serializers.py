from rest_framework import serializers

from .models import (
    CorrectiveAction,
    Inspection,
    InspectionChecklist,
    InspectionItemResult,
    InspectionPlan,
    NonConformanceReport,
    QualityAudit,
    SamplingPlan,
    SupplierQualityScore,
    TestCertificate,
)


class InspectionPlanSerializer(serializers.ModelSerializer):
    checklist_count = serializers.IntegerField(source="checklists.count", read_only=True)

    class Meta:
        model = InspectionPlan
        fields = "__all__"
        read_only_fields = ("id", "reference", "created_by", "status", "created_at", "updated_at")


class InspectionChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChecklist
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InspectionItemResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionItemResult
        fields = "__all__"
        read_only_fields = ("id", "recorded_by", "recorded_at", "created_at", "updated_at")


class InspectionSerializer(serializers.ModelSerializer):
    item_results = InspectionItemResultSerializer(many=True, read_only=True)

    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ("id", "reference", "status", "started_at", "completed_at", "overall_result", "created_at", "updated_at")


class TestCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCertificate
        fields = "__all__"
        read_only_fields = ("id", "reference", "issued_by", "status", "issued_at", "created_at", "updated_at")


class NonConformanceReportSerializer(serializers.ModelSerializer):
    corrective_actions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = NonConformanceReport
        fields = "__all__"
        read_only_fields = ("id", "reference", "raised_by", "status", "raised_at", "closed_at", "created_at", "updated_at")


class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = "__all__"
        read_only_fields = ("id", "reference", "status", "approved_by", "approved_at", "verified_by", "verified_at", "closed_at", "created_at", "updated_at")


class QualityAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityAudit
        fields = "__all__"
        read_only_fields = ("id", "reference", "auditor", "status", "completed_at", "created_at", "updated_at")


class SupplierQualityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQualityScore
        fields = "__all__"
        read_only_fields = ("id", "score", "inspection_count", "inspection_pass_rate", "ncr_count", "capa_overdue_count", "computed_at", "computed_by", "created_at", "updated_at")


class SamplingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SamplingPlan
        fields = "__all__"
        read_only_fields = ("id", "reference", "created_by", "status", "created_at", "updated_at")
