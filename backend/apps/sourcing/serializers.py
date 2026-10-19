from rest_framework import serializers

from .models import (
    AuctionBid,
    BidEvaluation,
    BidLineItem,
    BidPackage,
    EvaluationCriterion,
    ReverseAuction,
    SourcingProject,
    SupplierInvitation,
    Tender,
    TenderDocument,
    TenderLot,
    TenderResponse,
)


class SourcingProjectSerializer(serializers.ModelSerializer):
    tender_count = serializers.IntegerField(source="tenders.count", read_only=True)

    class Meta:
        model = SourcingProject
        fields = "__all__"
        read_only_fields = ("id", "reference", "owner", "status", "created_at", "updated_at")


class TenderLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderLot
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TenderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocument
        fields = "__all__"
        read_only_fields = ("id", "uploaded_by", "created_at", "updated_at")


class BidLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidLineItem
        fields = "__all__"
        read_only_fields = ("id", "line_total", "created_at", "updated_at")


class BidEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidEvaluation
        fields = "__all__"
        read_only_fields = ("id", "evaluator", "evaluated_at", "created_at", "updated_at")


class TenderResponseSerializer(serializers.ModelSerializer):
    lines = BidLineItemSerializer(many=True, read_only=True)
    evaluations = BidEvaluationSerializer(many=True, read_only=True)

    class Meta:
        model = TenderResponse
        fields = "__all__"
        read_only_fields = ("id", "reference", "supplier", "status", "subtotal", "total", "weighted_score", "submitted_at", "created_at", "updated_at")


class BidPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidPackage
        fields = "__all__"
        read_only_fields = ("id", "status", "issued_at", "downloaded_at", "created_at", "updated_at")


class TenderSerializer(serializers.ModelSerializer):
    lots = TenderLotSerializer(many=True, read_only=True)
    documents = TenderDocumentSerializer(many=True, read_only=True)
    criteria = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    response_count = serializers.IntegerField(source="responses.count", read_only=True)

    class Meta:
        model = Tender
        fields = "__all__"
        read_only_fields = ("id", "reference", "buyer", "status", "published_at", "awarded_response", "created_at", "updated_at")


class EvaluationCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AuctionBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionBid
        fields = "__all__"
        read_only_fields = ("id", "bidder", "placed_at", "is_winning", "created_at", "updated_at")


class ReverseAuctionSerializer(serializers.ModelSerializer):
    bids = AuctionBidSerializer(many=True, read_only=True)

    class Meta:
        model = ReverseAuction
        fields = "__all__"
        read_only_fields = ("id", "reference", "buyer", "status", "current_best_bid", "current_best_bidder", "created_at", "updated_at")


class SupplierInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierInvitation
        fields = "__all__"
        read_only_fields = ("id", "invited_by", "status", "invited_at", "responded_at", "created_at", "updated_at")
