from django.contrib import admin

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


class InspectionChecklistInline(admin.TabularInline):
    model = InspectionChecklist
    extra = 0


class InspectionItemResultInline(admin.TabularInline):
    model = InspectionItemResult
    extra = 0


class CorrectiveActionInline(admin.TabularInline):
    model = CorrectiveAction
    extra = 0


@admin.register(InspectionPlan)
class InspectionPlanAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "created_by", "supplier", "status", "category")
    list_filter = ("status", "category")
    search_fields = ("reference", "title")
    inlines = (InspectionChecklistInline,)


@admin.register(InspectionChecklist)
class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ("title", "plan", "is_mandatory", "order")
    list_filter = ("is_mandatory",)


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "supplier", "inspector", "status", "scheduled_at", "overall_result")
    list_filter = ("status", "overall_result")
    search_fields = ("reference", "title")
    inlines = (InspectionItemResultInline,)


@admin.register(InspectionItemResult)
class InspectionItemResultAdmin(admin.ModelAdmin):
    list_display = ("inspection", "item_name", "result", "recorded_by", "recorded_at")
    list_filter = ("result",)


@admin.register(TestCertificate)
class TestCertificateAdmin(admin.ModelAdmin):
    list_display = ("reference", "certificate_number", "supplier", "issued_by", "status", "valid_until")
    list_filter = ("status",)
    search_fields = ("reference", "certificate_number")


@admin.register(NonConformanceReport)
class NonConformanceReportAdmin(admin.ModelAdmin):
    list_display = ("reference", "supplier", "raised_by", "severity", "status", "raised_at")
    list_filter = ("status", "severity")
    search_fields = ("reference", "description")
    inlines = (CorrectiveActionInline,)


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ("reference", "ncr", "action_type", "owner", "status", "due_date")
    list_filter = ("status", "action_type")
    search_fields = ("reference", "description")


@admin.register(QualityAudit)
class QualityAuditAdmin(admin.ModelAdmin):
    list_display = ("reference", "supplier", "auditor", "audit_type", "status", "rating")
    list_filter = ("status", "audit_type")
    search_fields = ("reference",)


@admin.register(SupplierQualityScore)
class SupplierQualityScoreAdmin(admin.ModelAdmin):
    list_display = ("supplier", "period", "score", "inspection_count", "inspection_pass_rate", "ncr_count")
    list_filter = ("period",)
    search_fields = ("supplier__email",)


@admin.register(SamplingPlan)
class SamplingPlanAdmin(admin.ModelAdmin):
    list_display = ("reference", "supplier", "product_description", "standard", "sample_size", "status")
    list_filter = ("status", "standard")
    search_fields = ("reference", "product_description")
