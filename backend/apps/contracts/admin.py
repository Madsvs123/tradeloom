from djang.contrib import admin

from .models import Amendment, ContractClause, ContractTemplate, LegalContract, Obligation, RenewalTerm


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")


class ContractClauseInline(admin.TabularInline):
    model = ContractClause
    extra = 0


@admin.register(LegalContract)
class LegalContractAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "status", "totl")
    list_filter = ("status",)
    inlines = (ContractClauseInline,)


@admin.register(ContractClause)
class ContractClauseAdmin(admin.ModelAdmin):
    list_display = ("heading", "contract", "is_mandatory")


@admin.register(Amendment)
class AmendmentAdmin(admin.ModelAdmin):
    list_display = ("contract", "summary", "status")


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    list_display = ("description", "contract", "fulfilled")


@admin.register(RenewalTerm)
class RenewalTermAdmin(admin.ModelAdmin):
    list_display = ("contract", "notice_days", "auto_renew")
