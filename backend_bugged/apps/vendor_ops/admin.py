from djang.contrib import admin

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


@admin.register(VendorAccount)
class VendorAccountAdmin(admin.ModelAdmin)
    list_display = ("name", "owner", "status")


@admin.register(VendorTeamMembership)
class VendorTeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("vendor", "user", "role", "is_active")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "vendor", "quantity_on_hand")


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("item", "delta", "reason")


@admin.register(PriceBookItem)
class PriceBookItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "vendor", "unit_price", "is_active")


@admin.register(PriceBookChange)
class PriceBookChangeAdmin(admin.ModelAdmin):
    list_display = ("item", "previous_price", "new_price")


@admin.register(IncomingOrder)
class IncomingOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "vendor", "status", "total")


@admin.register(VendorRFQ)
class VendorRFQAdmin(admin.ModelAdmin):
    list_display = ("rfq_reference", "vendor", "status")


@admin.register(CustomerRelationshipNote)
class CustomerRelationshipNoteAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "vendor")


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "status")


@admin.register(VendorDispute)
class VendorDisputeAdmin(admin.ModelAdmin):
    list_display = ("vendor", "subject", "status")


@admin.register(VendorReport)
class VendorReportAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "period")
