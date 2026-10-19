from django.contrib import admin

from .models import (
    AdvancedShippingNotice,
    CarrierAccount,
    Carton,
    CustomsDocument,
    DamageClaim,
    DeliveryAppointment,
    Dock,
    FreightQuote,
    HazardousDeclaration,
    Incoterm,
    InventoryCount,
    LogisticsException,
    PackingList,
    Pallet,
    RateTable,
    ReceivingInspection,
    RouteMilestone,
    ShipmentDocument,
    ShipmentPlan,
    TrackingEvent,
    Warehouse,
    WarehouseBin,
    WarehouseZone,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "county", "city", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name", "code", "city")


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "code", "name", "zone_type", "is_active")
    list_filter = ("zone_type", "is_active")


@admin.register(WarehouseBin)
class WarehouseBinAdmin(admin.ModelAdmin):
    list_display = ("zone", "code", "capacity", "is_active")
    list_filter = ("is_active",)


@admin.register(Dock)
class DockAdmin(admin.ModelAdmin):
    list_display = ("name", "warehouse", "dock_type", "is_active")
    list_filter = ("dock_type", "is_active")


@admin.register(CarrierAccount)
class CarrierAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "scac", "account_number", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "scac")


@admin.register(RateTable)
class RateTableAdmin(admin.ModelAdmin):
    list_display = ("name", "carrier", "origin", "destination", "base_rate", "status")
    list_filter = ("status", "currency")


@admin.register(Incoterm)
class IncotermAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(FreightQuote)
class FreightQuoteAdmin(admin.ModelAdmin):
    list_display = ("carrier", "origin", "destination", "amount", "status", "valid_until")
    list_filter = ("status",)


@admin.register(ShipmentPlan)
class ShipmentPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "carrier", "status", "origin", "destination")
    list_filter = ("status",)


@admin.register(AdvancedShippingNotice)
class AdvancedShippingNoticeAdmin(admin.ModelAdmin):
    list_display = ("number", "shipment_plan", "status", "sent_at")
    list_filter = ("status",)


@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ("number", "shipment_plan", "package_count", "gross_weight_kg")


@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    list_display = ("sscc", "packing_list", "weight_kg")


@admin.register(Carton)
class CartonAdmin(admin.ModelAdmin):
    list_display = ("sku", "quantity", "packing_list", "pallet")


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "status", "location", "occurred_at")
    list_filter = ("status",)


@admin.register(DeliveryAppointment)
class DeliveryAppointmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "dock", "scheduled_at", "status")
    list_filter = ("status",)


@admin.register(ReceivingInspection)
class ReceivingInspectionAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "inspector", "status")
    list_filter = ("status",)


@admin.register(InventoryCount)
class InventoryCountAdmin(admin.ModelAdmin):
    list_display = ("number", "warehouse", "zone", "status", "counted_at", "reconciled_at")
    list_filter = ("status",)


@admin.register(ShipmentDocument)
class ShipmentDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "shipment_plan", "document_type", "status", "verified_at")
    list_filter = ("status", "document_type")


@admin.register(HazardousDeclaration)
class HazardousDeclarationAdmin(admin.ModelAdmin):
    list_display = ("un_number", "proper_shipping_name", "hazard_class", "shipment_plan", "status")
    list_filter = ("status", "hazard_class")


@admin.register(DamageClaim)
class DamageClaimAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "claimed_amount", "status")
    list_filter = ("status",)


@admin.register(RouteMilestone)
class RouteMilestoneAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "name", "sequence", "completed_at")


@admin.register(CustomsDocument)
class CustomsDocumentAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "document_type", "reference", "cleared")
    list_filter = ("cleared",)


@admin.register(LogisticsException)
class LogisticsExceptionAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "code", "status", "resolved_at")
    list_filter = ("status",)
