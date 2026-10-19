from django.contrib import admin

from .models import (
    ApprovalRule,
    ApprovalWorkflow,
    BudgetLine,
    BuyingCommittee,
    BuyingCommitteeMember,
    ContractCoverageCheck,
    DepartmentBudget,
    PolicyRule,
    PreferredSupplierProgram,
    ProcurementEvent,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchasingPolicy,
    RequisitionToRFQConversion,
    SavingsTracking,
    SourcingRequest,
    SpendCategory,
    SpendControl,
    Supplier,
    SupplierOnboardingChecklist,
    SupplierScorecard,
)


@admin.register(DepartmentBudget)
class DepartmentBudgetAdmin(admin.ModelAdmin):
    list_display = ("department", "fiscal_year", "allocated", "spent")


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
    list_display = ("name", "status", "county")
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


@admin.register(SourcingRequest)
class SourcingRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "requester", "status", "estimated_value", "required_by")
    list_filter = ("status",)
    search_fields = ("reference", "title", "requester__email")


@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ("name", "budget", "category", "allocated", "committed", "spent")
    list_filter = ("is_active",)


@admin.register(PolicyRule)
class PolicyRuleAdmin(admin.ModelAdmin):
    list_display = ("policy", "rule_type", "threshold_amount", "min_quotes", "is_active")
    list_filter = ("rule_type", "is_active")


@admin.register(ContractCoverageCheck)
class ContractCoverageCheckAdmin(admin.ModelAdmin):
    list_display = ("requisition", "contract_number", "is_covered", "coverage_type", "checked_by")
    list_filter = ("is_covered",)


@admin.register(SpendCategory)
class SpendCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(SavingsTracking)
class SavingsTrackingAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "savings_type", "status", "estimated_amount", "realized_amount")
    list_filter = ("savings_type", "status")
    search_fields = ("reference", "title")
