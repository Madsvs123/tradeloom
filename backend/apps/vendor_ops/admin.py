from django.contrib import admin

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


@admin.register(VendorAccount)
class VendorAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "owner", "status", "country")
    list_filter = ("status", "country")
    search_fields = ("name", "legal_name")


@admin.register(VendorTeamMembership)
class VendorTeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("vendor", "user", "role", "is_active")
    list_filter = ("role", "is_active")


@admin.register(VendorPerformanceRecord)
class VendorPerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ("vendor", "period", "overall_score", "status", "published_at")
    list_filter = ("status",)


@admin.register(VendorScorecard)
class VendorScorecardAdmin(admin.ModelAdmin):
    list_display = ("vendor", "period", "score", "band", "status", "decided_at")
    list_filter = ("status", "band")


@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "vendor", "document_type", "status", "expires_at", "verified_at")
    list_filter = ("status", "document_type")


@admin.register(PriceChangeRequest)
class PriceChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("price_book_item", "requested_price", "currency", "status", "decided_at")
    list_filter = ("status",)


@admin.register(VendorAnnouncement)
class VendorAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "vendor", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active",)


@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ("vendor", "rating", "order_number", "customer_name", "is_public")
    list_filter = ("rating", "is_public")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "vendor", "name", "quantity_on_hand", "quantity_reserved", "reorder_point")
    search_fields = ("sku", "name")


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("item", "delta", "reason", "actor", "created_at")


@admin.register(PriceBookItem)
class PriceBookItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "vendor", "unit_price", "currency", "is_active")
    list_filter = ("is_active",)


@admin.register(PriceBookChange)
class PriceBookChangeAdmin(admin.ModelAdmin):
    list_display = ("item", "previous_price", "new_price", "actor", "created_at")


@admin.register(IncomingOrder)
class IncomingOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "vendor", "buyer_name", "status", "total", "due_at")
    list_filter = ("status",)


@admin.register(VendorRFQ)
class VendorRFQAdmin(admin.ModelAdmin):
    list_display = ("rfq_reference", "vendor", "title", "status", "quoted_total", "due_at")
    list_filter = ("status",)


@admin.register(CustomerRelationshipNote)
class CustomerRelationshipNoteAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "vendor", "author", "created_at")


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "currency", "status", "reference")
    list_filter = ("status",)


@admin.register(VendorDispute)
class VendorDisputeAdmin(admin.ModelAdmin):
    list_display = ("vendor", "subject", "order_number", "amount", "status")
    list_filter = ("status",)


@admin.register(VendorReport)
class VendorReportAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "period")
