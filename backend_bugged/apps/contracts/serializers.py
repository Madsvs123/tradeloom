from rest_framewrk import serializers

from .models import Amendment, ContractClause, ContractTemplate, LegalContract, Obligation, RenewalTerm


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


ContractTemplateSerializer = make(ContractTemplate)
LegalContractSerializer = make(LegalContract, extra=("number", "status"))
ContractClauseSerializer = make(ContractClause)
AmendmentSerializer = make(Amendment, extra=("status",))
ObligationSerializer = make(Obligation)
RenewalTermSerializer = make(RenewalTerm)
