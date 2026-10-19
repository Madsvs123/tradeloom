from rest_framework import serializers

from .models import (
    EvaluationCriterion,
    EvaluationScore,
    NegotiationMessage,
    NegotiationRoom,
    QuotationComparisonSnapshot,
    QuotationLineItem,
    RFQ,
    RFQAttachment,
    RFQDocument,
    RFQLineItem,
    RFQStatusHistory,
    RFQSupplier,
    RfqTemplate,
    SupplierCounterOffer,
    SupplierQuotation,
)


class RFQLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQLineItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RFQSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQSupplier
        fields = "__all__"
        read_only_fields = ("id", "invited_at", "responded_at", "created_at", "updated_at")


class RFQSerializer(serializers.ModelSerializer):
    line_items = RFQLineItemSerializer(many=True, read_only=True)
    invited_suppliers = RFQSupplierSerializer(many=True, read_only=True)

    class Meta:
        model = RFQ
        fields = "__all__"
        read_only_fields = ("id", "reference", "buyer", "status", "awarded_quotation", "created_at", "updated_at")


class QuotationLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLineItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierQuotationSerializer(serializers.ModelSerializer):
    lines = QuotationLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = SupplierQuotation
        fields = "__all__"
        read_only_fields = ("id", "status", "subtotal", "total", "submitted_at", "created_at", "updated_at")


class NegotiationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationMessage
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at", "updated_at")


class SupplierCounterOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCounterOffer
        fields = "__all__"
        read_only_fields = ("id", "status", "created_by", "created_at", "updated_at")


class RFQAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQAttachment
        fields = "__all__"
        read_only_fields = ("id", "uploaded_by", "created_at", "updated_at")


class RFQStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQStatusHistory
        fields = "__all__"
        read_only_fields = fields


class RfqTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfqTemplate
        fields = "__all__"
        read_only_fields = ("id", "status", "owner", "created_at", "updated_at")


class EvaluationCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EvaluationScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationScore
        fields = "__all__"
        read_only_fields = ("id", "scored_by", "passed", "created_at", "updated_at")


class QuotationComparisonSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationComparisonSnapshot
        fields = "__all__"
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class RfqDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfqDocument
        fields = "__all__"
        read_only_fields = ("id", "uploaded_by", "created_at", "updated_at")


class NegotiationRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRoom
        fields = "__all__"
        read_only_fields = ("id", "rfq", "status", "opened_by", "opened_at", "closed_at", "created_at", "updated_at")
