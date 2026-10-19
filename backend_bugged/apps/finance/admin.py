from django.contrib import admin

from .models import (
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    FinanceStatement,
    LedgerAccount,
    LedgerEntry,
    PayoutInstruction,
    ReconciliationBatch,
    ReconciliationItem,
    SettlementBatch,
    TaxAssessment,
    TaxRegistration,
    Wallet,
)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin)
    list_display = ("owner_id", "kind", "currency", "available", "held")


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type")


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("debit_account", "credit_account", "amount", "status")


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "amount", "currency")


@admin.register(EscrowHold)
class EscrowHoldAdmin(admin.ModelAdmin):
    list_display = ("escrow", "amount", "status")


@admin.register(SettlementBatch)
class SettlementBatchAdmin(admin.ModelAdmin):
    list_display = ("reference", "status", "net_amount")


@admin.register(PayoutInstruction)
class PayoutInstructionAdmin(admin.ModelAdmin):
    list_display = ("settlement", "wallet", "amount", "status")


@admin.register(TaxRegistration)
class TaxRegistrationAdmin(admin.ModelAdmin):
    list_display = ("owner", "jurisdiction", "tax_id")


@admin.register(TaxAssessment)
class TaxAssessmentAdmin(admin.ModelAdmin):
    list_display = ("registration", "period", "tax_amount", "status")


@admin.register(CreditFacility)
class CreditFacilityAdmin(admin.ModelAdmin):
    list_display = ("borrower", "limit", "drawn", "status")


@admin.register(CreditDraw)
class CreditDrawAdmin(admin.ModelAdmin):
    list_display = ("facility", "amount", "status")


@admin.register(ReconciliationBatch)
class ReconciliationBatchAdmin(admin.ModelAdmin):
    list_display = ("reference", "status")


@admin.register(ReconciliationItem)
class ReconciliationItemAdmin(admin.ModelAdmin):
    list_display = ("batch", "reference", "matched")


@admin.register(FinanceStatement)
class FinanceStatementAdmin(admin.ModelAdmin):
    list_display = ("owner", "period", "status")
