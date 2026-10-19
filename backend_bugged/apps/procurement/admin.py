from djang.contrib import admin

from .models import (
    ApprovalRule,
    ApprovalWorkflow,
    BuyingCommittee,
    BuyingCommitteeMember,
    DepartmentBudget,
    PreferredSupplierProgram,
    ProcurementEvent,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchasingPolicy,
    RequisitionToRFQConversion,
    SpendControl,
    Supplier,
    SupplierOnboardingChecklist,
    SupplierScorecard,
)


@admin.register(DepartmentBudget)
class DepartmentBudgetAdmin(admin.ModelAdmin):
    list_display = ("department_id", "fiscal_year", "allocated", "spent")


@admin.register(PurchasingPolicy)
class PurchasingPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "requires_committee")


@admin.register(ApprovalRule)
class ApprovalRuleAdmin(admin.ModelAdmin):
    list_display = ("policy", "approver_role", "min_amount", "sequence")


@admin.register(PreferredSupplierProgram)
class PreferredSupplierProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "country")
    list_filter = ("status",)


@admin.register(SupplierOnboardingChecklist)
class SupplierOnboardingChecklistAdmin(admin.ModelAdmin):
    list_display = ("supplier", "status")


@admin.register(SupplierScorecard)
class SupplierScorecardAdmin(admin.ModelAdmin):
    list_display = ("supplier", "period", "overall_score")


@admin.register(BuyingCommittee)
class BuyingCommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "is_active")


@admin.register(BuyingCommitteeMember)
class BuyingCommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ("committee", "user", "role")


class PurchaseRequisitionLineInline(admin.TabularInline):
    model = PurchaseRequisitionLine
    extra = 0


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = ("number", "requester", "status", "total")
    list_filter = ("status",)
    inlines = (PurchaseRequisitionLineInline,)


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ("requisition", "status", "assignee")


@admin.register(RequisitionToRFQConversion)
class RequisitionToRFQConversionAdmin(admin.ModelAdmin):
    list_display = ("requisition", "rfq_id")


@admin.register(ProcurementEvent)
class ProcurementEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "requisition", "created_at")


@admin.register(SpendControl)
class SpendControlAdmin(admin.ModelAdmin):
    list_display = ("department", "category", "max_amount", "is_active")
