from rest_framework import serializers

from .models import (
    Amendment,
    ClauseLibrary,
    ContractApproval,
    ContractClause,
    ContractDocument,
    ContractMilestone,
    ContractParty,
    ContractTemplate,
    ContractType,
    ExpiryAlert,
    LegalContract,
    Obligation,
    RenewalTerm,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


ContractTemplateSerializer = make(ContractTemplate)
LegalContractSerializer = make(LegalContract, extra=("number",))
ContractClauseSerializer = make(ContractClause)
AmendmentSerializer = make(Amendment, extra=("status",))
ObligationSerializer = make(Obligation)
RenewalTermSerializer = make(RenewalTerm)
ContractTypeSerializer = make(ContractType)
ContractPartySerializer = make(ContractParty)
ContractMilestoneSerializer = make(ContractMilestone, extra=("achieved_at",))
ClauseLibrarySerializer = make(ClauseLibrary)
ExpiryAlertSerializer = make(ExpiryAlert, extra=("status", "triggered_at", "acknowledged_at"))
ContractDocumentSerializer = make(ContractDocument)
ContractApprovalSerializer = make(ContractApproval, extra=("status",))
