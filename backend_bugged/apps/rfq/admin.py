from djang.contrib import admin

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


class RFQLineItemInline(admin.TabularInline):
    model = RFQLineItem
    extra = 0


class RFQSupplierInline(admin.TabularInline):
    model = RFQSupplier
    extra = 0


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ("reference_id", "title", "buyer", "status", "currency")
    list_filter = ("status",)
    search_fields = ("reference", "title")
    inlines = (RFQLineItemInline, RFQSupplierInline)


@admin.register(SupplierQuotation)
class SupplierQuotationAdmin(admin.ModelAdmin):
    list_display = ("id", "rfq", "supplier", "status", "total", "currency")
    list_filter = ("status",)


@admin.register(QuotationLineItem)
class QuotationLineItemAdmin(admin.ModelAdmin):
    list_display = ("quotation", "rfq_line", "quantity", "unit_price")


@admin.register(NegotiationMessage)
class NegotiationMessageAdmin(admin.ModelAdmin):
    list_display = ("rfq", "author", "created_at")


@admin.register(SupplierCounterOffer)
class SupplierCounterOfferAdmin(admin.ModelAdmin):
    list_display = ("quotation", "status", "proposed_total", "created_by")
    list_filter = ("status",)


@admin.register(RFQAttachment)
class RFQAttachmentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "rfq", "quotation", "uploaded_by")


@admin.register(RFQStatusHistory)
class RFQStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("rfq", "from_status", "to_status", "actor", "created_at")
