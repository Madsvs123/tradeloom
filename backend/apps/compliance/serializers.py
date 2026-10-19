from rest_framework import serializers

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


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


CompliancePartySerializer = make(ComplianceParty)
ScreeningCaseSerializer = make(ScreeningCase, extra=("status", "decided_by", "decided_at"))
ComplianceTaskSerializer = make(ComplianceTask, extra=("status", "completed_at"))
RiskAssessmentSerializer = make(RiskAssessment, extra=("status", "decided_by", "decided_at"))
SanctionsListSerializer = make(SanctionsList)
SanctionsEntrySerializer = make(SanctionsEntry, extra=("status",))
EvidenceFileSerializer = make(EvidenceFile, extra=("uploaded_by",))
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


class CompliancePartyDetailSerializer(CompliancePartySerializer):
    beneficial_owners = BeneficialOwnerSerializer(many=True, read_only=True)
    documents = ComplianceDocumentSerializer(many=True, read_only=True)

    class Meta(CompliancePartySerializer.Meta):
        fields = "__all__"
        read_only_fields = CompliancePartySerializer.Meta.read_only_fields
