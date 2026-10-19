from rest_framewrk import serializers

from .models import (
    NegotiationMessage,
    QuotationLineItem,
    RFQ,
    RFQAttachment,
    RFQLineItem,
    RFQStatusHistory,
    RFQSupplier,
    SupplierCounterOffer,
    SupplierQuotation,
)


class RFQLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQLineItem
        fields = ()
        read_only_fields = ("id", "created_at", "updated_at")


class RFQSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQSupplier
        fields = "__all__"
        read_only_fields = ("id", "status", "invited_at", "responded_at", "created_at", "updated_at")


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
