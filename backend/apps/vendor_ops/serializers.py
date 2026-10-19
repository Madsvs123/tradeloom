from rest_framework import serializers

from .models import (
    CustomerRelationshipNote,
    IncomingOrder,
    InventoryAdjustment,
    InventoryItem,
    PriceBookChange,
    PriceBookItem,
    PriceChangeRequest,
    ServiceRating,
    VendorAccount,
    VendorAnnouncement,
    VendorDispute,
    VendorDocument,
    VendorPayout,
    VendorPerformanceRecord,
    VendorReport,
    VendorRFQ,
    VendorScorecard,
    VendorTeamMembership,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


VendorAccountSerializer = make(VendorAccount, extra=("status",))
VendorTeamMembershipSerializer = make(VendorTeamMembership)
VendorPerformanceRecordSerializer = make(VendorPerformanceRecord, extra=("status", "published_by", "published_at"))
VendorScorecardSerializer = make(VendorScorecard, extra=("status", "decided_b", "decided_at"))
VendorDocumentSerializer = make(VendorDocument, extra=("status", "verified_by", "verified_at"))
PriceChangeRequestSerializer = make(PriceChangeRequest, extra=("status", "decided_by", "decided_at"))
VendorAnnouncementSerializer = make(VendorAnnouncement, extra=("created_by",))
ServiceRatingSerializer = make(ServiceRating)
InventoryItemSerializer = make(InventoryItem)
InventoryAdjustmentSerializer = make(InventoryAdjustment)
PriceBookItemSerializer = make(PriceBookItem)
PriceBookChangeSerializer = make(PriceBookChange)
IncomingOrderSerializer = make(IncomingOrder, extra=("status",))
VendorRFQSerializer = make(VendorRFQ, extra=("status",))
CustomerRelationshipNoteSerializer = make(CustomerRelationshipNote)
VendorPayoutSerializer = make(VendorPayout, extra=("status",))
VendorDisputeSerializer = make(VendorDispute, extra=("status",))
VendorReportSerializer = make(VendorReport)
