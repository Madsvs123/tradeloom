from django.contrib import admin

from .models import (
    BankGuarantee,
    CreditInsurancePolicy,
    FactoringAgreement,
    FinanceDisbursement,
    FinancingOffer,
    InvoiceFinancingRequest,
    LcAmendment,
    LetterOfCredit,
    RepaymentSchedule,
)


class LcAmendmentInline(admin.TabularInline):
    model = LcAmendment
    extra = 0


class FinancingOfferInline(admin.TabularInline):
    model = FinancingOffer
    extra = 0


class FinanceDisbursementInline(admin.TabularInline):
    model = FinanceDisbursement
    extra = 0


class RepaymentScheduleInline(admin.TabularInline):
    model = RepaymentSchedule
    extra = 0


@admin.register(LetterOfCredit)
class LetterOfCreditAdmin(admin.ModelAdmin):
    list_display = ("reference", "applicant", "beneficiary", "lc_type", "status", "amount", "currency", "expiry_date")
    list_filter = ("status", "lc_type", "currency")
    search_fields = ("reference", "issuing_bank")
    inlines = (LcAmendmentInline,)


@admin.register(LcAmendment)
class LcAmendmentAdmin(admin.ModelAdmin):
    list_display = ("lc", "amendment_type", "status", "requested_by", "requested_at")
    list_filter = ("status",)


@admin.register(BankGuarantee)
class BankGuaranteeAdmin(admin.ModelAdmin):
    list_display = ("reference", "applicant", "beneficiary", "guarantee_type", "status", "amount", "expiry_date")
    list_filter = ("status", "guarantee_type")
    search_fields = ("reference", "bank")


@admin.register(InvoiceFinancingRequest)
class InvoiceFinancingRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "applicant", "invoice_reference", "invoice_amount", "requested_amount", "status")
    list_filter = ("status", "currency")
    search_fields = ("reference", "invoice_reference")
    inlines = (FinancingOfferInline, FinanceDisbursementInline, RepaymentScheduleInline)


@admin.register(FinancingOffer)
class FinancingOfferAdmin(admin.ModelAdmin):
    list_display = ("request", "offered_by", "status", "amount", "rate", "tenor_days", "issued_at")
    list_filter = ("status",)


@admin.register(FactoringAgreement)
class FactoringAgreementAdmin(admin.ModelAdmin):
    list_display = ("reference", "supplier", "factor", "agreement_type", "status", "credit_limit")
    list_filter = ("status", "agreement_type")


@admin.register(CreditInsurancePolicy)
class CreditInsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ("reference", "insured", "insurer", "policy_number", "status", "coverage_limit", "end_date")
    list_filter = ("status",)


@admin.register(FinanceDisbursement)
class FinanceDisbursementAdmin(admin.ModelAdmin):
    list_display = ("reference", "request", "agreement", "recipient", "status", "amount", "disbursed_at")
    list_filter = ("status", "method")


@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ("request", "due_date", "principal", "interest", "total_due", "status", "paid_at")
    list_filter = ("status",)
