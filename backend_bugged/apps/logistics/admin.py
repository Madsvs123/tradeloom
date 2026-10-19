from djang.contrib import admin

from .models import (
    AdvancedShippingNotice,
    CarrierAccount,
    Carton,
    CustomsDocument,
    DamageClaim,
    DeliveryAppointment,
    Dock,
    FreightQuote,
    Incoterm,
    LogisticsException,
    PackingList,
    Pallet,
    ReceivingInspection,
    RouteMilestone,
    ShipmentPlan,
    TrackingEvent,
    Warehouse,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin)
    list_display = ("name", "code", "country", "is_active")


@admin.register(Dock)
class DockAdmin(admin.ModelAdmin):
    list_display = ("name", "warehouse", "dock_type")


@admin.register(CarrierAccount)
class CarrierAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "scac", "is_active")


@admin.register(Incoterm)
class IncotermAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(FreightQuote)
class FreightQuoteAdmin(admin.ModelAdmin):
    list_display = ("carrier", "origin", "destination", "amount", "status")


@admin.register(ShipmentPlan)
class ShipmentPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "status", "destination")


@admin.register(AdvancedShippingNotice)
class AdvancedShippingNoticeAdmin(admin.ModelAdmin):
    list_display = ("number", "shipment_plan", "status")


@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ("number", "shipment_plan", "package_count")


@admin.register(Pallet)
class PalletAdmin(admin.ModelAdmin):
    list_display = ("sscc", "packing_list")


@admin.register(Carton)
class CartonAdmin(admin.ModelAdmin):
    list_display = ("sku", "quantity", "packing_list")


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "status", "occurred_at")


@admin.register(DeliveryAppointment)
class DeliveryAppointmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "scheduled_at", "status")


@admin.register(ReceivingInspection)
class ReceivingInspectionAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "status")


@admin.register(DamageClaim)
class DamageClaimAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "claimed_amount", "status")


@admin.register(RouteMilestone)
class RouteMilestoneAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "name", "sequence")


@admin.register(CustomsDocument)
class CustomsDocumentAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "document_type", "cleared")


@admin.register(LogisticsException)
class LogisticsExceptionAdmin(admin.ModelAdmin):
    list_display = ("shipment_plan", "code", "status")
