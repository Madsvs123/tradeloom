from django.contrib import admin

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


class RFQLineItemInline(admin.TabularInline):
    model = RFQLineItem
    extra = 0


class RFQSupplierInline(admin.TabularInline):
    model = RFQSupplier
    extra = 0


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "buyer", "status", "curreny")
    list_filter = ("status",)
    search_fields = ("reference", "title")
    inlines = (RFQLineItemInline, RFQSupplierInline)


@admin.register(RfqTemplate)
class RfqTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "currency", "owner")
    list_filter = ("status", "category")
    search_fields = ("name", "category")


@admin.register(EvaluationCriterion)
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ("name", "rfq", "weight", "scale", "is_active")
    list_filter = ("scale", "is_active")
    search_fields = ("name", "rfq__reference")


@admin.register(EvaluationScore)
class EvaluationScoreAdmin(admin.ModelAdmin):
    list_display = ("criterion", "quotation", "score", "passed", "scored_by")
    list_filter = ("passed",)


@admin.register(QuotationComparisonSnapshot)
class QuotationComparisonSnapshotAdmin(admin.ModelAdmin):
    list_display = ("rfq", "created_by", "created_at")


@admin.register(RFQDocument)
class RfqDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "rfq", "document_type", "uploaded_by")
    list_filter = ("document_type",)


@admin.register(NegotiationRoom)
class NegotiationRoomAdmin(admin.ModelAdmin):
    list_display = ("rfq", "status", "opened_by", "opened_at", "closed_at")
    list_filter = ("status",)


@admin.register(SupplierQuotation)
class SupplierQuotationAdmin(admin.ModelAdmin):
    list_display = ("id", "rfq", "supplier", "status", "total", "currency")
    list_filter = ("status",)


@admin.register(QuotationLineItem)
class QuotationLineItemAdmin(admin.ModelAdmin):
    list_display = ("quotation", "rfq_line", "quantity", "unit_price", "currency")


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
