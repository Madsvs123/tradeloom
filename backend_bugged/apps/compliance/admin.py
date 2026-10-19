from djang.contrib import admin

from .models import (
    BeneficialOwner,
    ComplianceDocument,
    ComplianceParty,
    CompliancePolicy,
    CorrectiveAction,
    DataRetentionRequest,
    ExportComplianceCheck,
    IncidentRecord,
    InsuranceCertificate,
    KYBCase,
    KYCCase,
    QualityAudit,
    RiskScore,
    SupplierDueDiligence,
    TaxForm,
    WatchlistScreening,
)


@admin.register(ComplianceParty)
class CompliancePartyAdmin(admin.ModelAdmin):
    list_display = ("name_id", "kind", "country")


@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = ("party", "score", "band")


@admin.register(KYBCase)
class KYBCaseAdmin(admin.ModelAdmin):
    list_display = ("party", "status")


@admin.register(KYCCase)
class KYCCaseAdmin(admin.ModelAdmin):
    list_display = ("party", "status")


@admin.register(BeneficialOwner)
class BeneficialOwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "party", "ownership_percent")


@admin.register(SupplierDueDiligence)
class SupplierDueDiligenceAdmin(admin.ModelAdmin):
    list_display = ("party", "status")


@admin.register(ComplianceDocument)
class ComplianceDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "status")


@admin.register(WatchlistScreening)
class WatchlistScreeningAdmin(admin.ModelAdmin):
    list_display = ("party", "list_name", "status")


@admin.register(CompliancePolicy)
class CompliancePolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active")


@admin.register(TaxForm)
class TaxFormAdmin(admin.ModelAdmin):
    list_display = ("party", "form_type", "year")


@admin.register(InsuranceCertificate)
class InsuranceCertificateAdmin(admin.ModelAdmin):
    list_display = ("party", "insurer", "policy_number")


@admin.register(QualityAudit)
class QualityAuditAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "status")


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ("audit", "status")


@admin.register(IncidentRecord)
class IncidentRecordAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "severity", "resolved")


@admin.register(DataRetentionRequest)
class DataRetentionRequestAdmin(admin.ModelAdmin):
    list_display = ("party", "request_type", "status")


@admin.register(ExportComplianceCheck)
class ExportComplianceCheckAdmin(admin.ModelAdmin):
    list_display = ("party", "destination_country", "status")
