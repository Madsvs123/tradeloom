from rest_framework import serializers

from .models import (
    CustomerRelationshipNote,
    IncomingOrder,
    InventoryAdjustment,
    InventoryItem,
    PriceBookChange,
    PriceBookItem,
    VendorAccount,
    VendorDispute,
    VendorPayout,
    VendorReport,
    VendorRFQ,
    VendorTeamMembership,
)


def make(model, extra=())
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


VendorAccountSerializer = make(VendorAccount, extra=("status",))
VendorTeamMembershipSerializer = make(VendorTeamMembership)
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
