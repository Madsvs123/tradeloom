from rest_framework import serializers

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


class LcAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LcAmendment
        fields = "__all__"
        read_only_fields = ("id", "status", "requested_by", "requested_at", "approved_by", "approved_at", "applied_at", "created_at", "updated_at")


class LetterOfCreditSerializer(serializers.ModelSerializer):
    amendments = LcAmendmentSerializer(many=True, read_only=True)

    class Meta:
        model = LetterOfCredit
        fields = "__all__"
        read_only_fields = ("id", "reference", "applicant", "status", "issued_at", "created_at", "updated_at")


class BankGuaranteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankGuarantee
        fields = "__all__"
        read_only_fields = ("id", "reference", "applicant", "status", "issue_date", "created_at", "updated_at")


class FinancingOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancingOffer
        fields = "__all__"
        read_only_fields = ("id", "offered_by", "status", "issued_at", "accepted_at", "created_at", "updated_at")


class FinanceDisbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceDisbursement
        fields = "__all__"
        read_only_fields = ("id", "reference", "recipient", "status", "disbursed_at", "created_at", "updated_at")


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = "__all__"
        read_only_fields = ("id", "request", "status", "paid_amount", "paid_at", "paid_by", "created_at", "updated_at")


class InvoiceFinancingRequestSerializer(serializers.ModelSerializer):
    offers = FinancingOfferSerializer(many=True, read_only=True)
    disbursements = FinanceDisbursementSerializer(many=True, read_only=True)
    repayment_schedules = RepaymentScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = InvoiceFinancingRequest
        fields = "__all__"
        read_only_fields = ("id", "reference", "applicant", "status", "submitted_at", "funded_at", "repaid_at", "created_at", "updated_at")


class FactoringAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoringAgreement
        fields = "__all__"
        read_only_fields = ("id", "reference", "supplier", "status", "signed_at", "created_at", "updated_at")


class CreditInsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditInsurancePolicy
        fields = "__all__"
        read_only_fields = ("id", "reference", "insured", "status", "created_at", "updated_at")
