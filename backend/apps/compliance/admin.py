from django.contrib import admin

from .models import (
    BeneficialOwner,
    ComplianceDocument,
    ComplianceParty,
    CompliancePolicy,
    ComplianceTask,
    CorrectiveAction,
    DataRetentionRequest,
    EvidenceFile,
    ExportComplianceCheck,
    IncidentRecord,
    InsuranceCertificate,
    KYBCase,
    KYCCase,
    QualityAudit,
    RiskAssessment,
    RiskScore,
    SanctionsEntry,
    SanctionsList,
    ScreeningCase,
    SupplierDueDiligence,
    TaxForm,
    WatchlistScreening,
)


@admin.register(ComplianceParty)
class CompliancePartyAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "country", "registration_number")
    list_filter = ("kind", "country")
    search_fields = ("name", "registration_number")


@admin.register(ScreeningCase)
class ScreeningCaseAdmin(admin.ModelAdmin):
    list_display = ("party", "list_name", "status", "assigned_to", "decided_at")
    list_filter = ("status",)


@admin.register(ComplianceTask)
class ComplianceTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "assignee", "priority", "status", "due_at")
    list_filter = ("status", "priority")


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("party", "methodology", "overall_score", "band", "status", "decided_at")
    list_filter = ("status", "band")


@admin.register(SanctionsList)
class SanctionsListAdmin(admin.ModelAdmin):
    list_display = ("name", "authority", "country", "list_type", "is_active")
    list_filter = ("list_type", "is_active")


@admin.register(SanctionsEntry)
class SanctionsEntryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "sanctions_list", "id_number", "country", "status")
    list_filter = ("status", "country")
    search_fields = ("full_name", "id_number")


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "case_type", "case_id", "uploaded_by")
    list_filter = ("case_type",)


@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = ("party", "score", "band", "created_at")
    list_filter = ("band",)


@admin.register(KYBCase)
class KYBCaseAdmin(admin.ModelAdmin):
    list_display = ("party", "status", "assigned_to", "decided_at")
    list_filter = ("status",)


@admin.register(KYCCase)
class KYCCaseAdmin(admin.ModelAdmin):
    list_display = ("party", "status", "assigned_to", "decided_at")
    list_filter = ("status",)


@admin.register(BeneficialOwner)
class BeneficialOwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "party", "ownership_percent", "nationality", "is_controlling")
    list_filter = ("is_controlling",)


@admin.register(SupplierDueDiligence)
class SupplierDueDiligenceAdmin(admin.ModelAdmin):
    list_display = ("party", "status", "completed_at")
    list_filter = ("status",)


@admin.register(ComplianceDocument)
class ComplianceDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "document_type", "status", "expires_at", "verified_at")
    list_filter = ("status", "document_type")
    search_fields = ("title", "document_type")


@admin.register(WatchlistScreening)
class WatchlistScreeningAdmin(admin.ModelAdmin):
    list_display = ("party", "list_name", "status")
    list_filter = ("status",)


@admin.register(CompliancePolicy)
class CompliancePolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active")
    search_fields = ("name",)


@admin.register(TaxForm)
class TaxFormAdmin(admin.ModelAdmin):
    list_display = ("party", "form_type", "year", "is_certified")


@admin.register(InsuranceCertificate)
class InsuranceCertificateAdmin(admin.ModelAdmin):
    list_display = ("party", "insurer", "policy_number", "expires_at")


@admin.register(QualityAudit)
class QualityAuditAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "status", "score", "scheduled_at")
    list_filter = ("status",)


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ("audit", "status", "due_at", "closed_at")
    list_filter = ("status",)


@admin.register(IncidentRecord)
class IncidentRecordAdmin(admin.ModelAdmin):
    list_display = ("title", "party", "severity", "occurred_at", "resolved")
    list_filter = ("severity", "resolved")


@admin.register(DataRetentionRequest)
class DataRetentionRequestAdmin(admin.ModelAdmin):
    list_display = ("party", "request_type", "status")
    list_filter = ("status",)


@admin.register(ExportComplianceCheck)
class ExportComplianceCheckAdmin(admin.ModelAdmin):
    list_display = ("party", "destination_country", "product_code", "status")
    list_filter = ("status",)
