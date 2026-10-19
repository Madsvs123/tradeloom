from rest_framework import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
        return Auto


CompliancePartySerializer = make(ComplianceParty)
RiskScoreSerializer = make(RiskScore)
KYBCaseSerializer = make(KYBCase, extra=("status", "decided_at"))
KYCCaseSerializer = make(KYCCase, extra=("status", "decided_at"))
BeneficialOwnerSerializer = make(BeneficialOwner)
SupplierDueDiligenceSerializer = make(SupplierDueDiligence, extra=("status", "completed_at"))
ComplianceDocumentSerializer = make(ComplianceDocument, extra=("status", "verified_at", "verified_by"))
WatchlistScreeningSerializer = make(WatchlistScreening)
CompliancePolicySerializer = make(CompliancePolicy)
TaxFormSerializer = make(TaxForm)
InsuranceCertificateSerializer = make(InsuranceCertificate)
QualityAuditSerializer = make(QualityAudit, extra=("status",))
CorrectiveActionSerializer = make(CorrectiveAction, extra=("status", "closed_at"))
IncidentRecordSerializer = make(IncidentRecord)
DataRetentionRequestSerializer = make(DataRetentionRequest, extra=("status",))
ExportComplianceCheckSerializer = make(ExportComplianceCheck, extra=("status",))
