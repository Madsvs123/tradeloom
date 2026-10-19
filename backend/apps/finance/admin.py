from django.contrib import admin

from .models import (
    BankAccount,
    CreditDraw,
    CreditFacility,
    EscrowAccount,
    EscrowHold,
    ExpenseCategory,
    FinanceApproval,
    FinanceStatement,
    InvoiceMatch,
    LedgerAccount,
    LedgerEntry,
    PaymentRun,
    PayoutInstruction,
    ReconciliationBatch,
    ReconciliationItem,
    SettlementBatch,
    TaxAssessment,
    TaxRegistration,
    TransactionTag,
    Wallet,
)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("owner", "kind", "currency", "availble", "held", "is_active")
    list_filter = ("kind", "currency", "is_active")
    search_fields = ("owner__email", "owner__username")


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "currency", "is_active")
    list_filter = ("account_type", "is_active")
    search_fields = ("code", "name")


@admin.register(TransactionTag)
class TransactionTagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "is_active")
    search_fields = ("name",)


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("reference", "debit_account", "credit_account", "amount", "status", "posted_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "memo")


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "status", "amount", "currency")
    list_filter = ("status", "currency")


@admin.register(EscrowHold)
class EscrowHoldAdmin(admin.ModelAdmin):
    list_display = ("escrow", "amount", "status")
    list_filter = ("status",)


@admin.register(SettlementBatch)
class SettlementBatchAdmin(admin.ModelAdmin):
    list_display = ("reference", "status", "gross_amount", "fee_amount", "net_amount")
    list_filter = ("status", "currency")


@admin.register(PaymentRun)
class PaymentRunAdmin(admin.ModelAdmin):
    list_display = ("reference", "description", "currency", "total_amount", "status", "executed_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "description")


@admin.register(PayoutInstruction)
class PayoutInstructionAdmin(admin.ModelAdmin):
    list_display = ("settlement", "payment_run", "wallet", "amount", "status", "sent_at")
    list_filter = ("status", "currency")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("account_name", "bank_name", "currency", "verified", "is_active")
    list_filter = ("verified", "is_active", "kind")
    search_fields = ("account_name", "bank_name", "account_number")


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")


@admin.register(InvoiceMatch)
class InvoiceMatchAdmin(admin.ModelAdmin):
    list_display = ("reference", "invoice_number", "expected_amount", "actual_amount", "variance", "status")
    list_filter = ("status", "currency")
    search_fields = ("reference", "invoice_number", "order_reference")


@admin.register(FinanceApproval)
class FinanceApprovalAdmin(admin.ModelAdmin):
    list_display = ("target_type", "target_id", "requested_by", "approver", "status", "decided_at")
    list_filter = ("status", "target_type")


@admin.register(TaxRegistration)
class TaxRegistrationAdmin(admin.ModelAdmin):
    list_display = ("owner", "jurisdiction", "tax_id", "is_active")
    search_fields = ("tax_id", "jurisdiction")


@admin.register(TaxAssessment)
class TaxAssessmentAdmin(admin.ModelAdmin):
    list_display = ("registration", "period", "tax_amount", "status", "filed_at")
    list_filter = ("status",)


@admin.register(CreditFacility)
class CreditFacilityAdmin(admin.ModelAdmin):
    list_display = ("borrower", "limit", "drawn", "currency", "status", "interest_rate")
    list_filter = ("status", "currency")


@admin.register(CreditDraw)
class CreditDrawAdmin(admin.ModelAdmin):
    list_display = ("facility", "amount", "status", "approved_at")
    list_filter = ("status",)


@admin.register(ReconciliationBatch)
class ReconciliationBatchAdmin(admin.ModelAdmin):
    list_display = ("reference", "status", "expected_amount", "actual_amount", "run_at")
    list_filter = ("status",)


@admin.register(ReconciliationItem)
class ReconciliationItemAdmin(admin.ModelAdmin):
    list_display = ("batch", "reference", "expected_amount", "actual_amount", "matched")
    list_filter = ("matched",)


@admin.register(FinanceStatement)
class FinanceStatementAdmin(admin.ModelAdmin):
    list_display = ("owner", "period", "currency", "status", "published_at")
    list_filter = ("status", "currency")
