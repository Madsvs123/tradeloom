from django.contrib import admin

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


class TenderLotInline(admin.TabularInline):
    model = TenderLot
    extra = 0


class TenderDocumentInline(admin.TabularInline):
    model = TenderDocument
    extra = 0


class BidLineItemInline(admin.TabularInline):
    model = BidLineItem
    extra = 0


class AuctionBidInline(admin.TabularInline):
    model = AuctionBid
    extra = 0


@admin.register(SourcingProject)
class SourcingProjectAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "owner", "status", "budget", "currency")
    list_filter = ("status",)
    search_fields = ("reference", "title", "category")


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "buyer", "status", "closing_at", "currency")
    list_filter = ("status",)
    search_fields = ("reference", "title")
    inlines = (TenderLotInline, TenderDocumentInline)


@admin.register(TenderLot)
class TenderLotAdmin(admin.ModelAdmin):
    list_display = ("tender", "lot_number", "name", "quantity", "unit", "target_price")
    list_filter = ("tender",)
    search_fields = ("name",)


@admin.register(TenderDocument)
class TenderDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "tender", "doc_type", "uploaded_by")
    list_filter = ("doc_type",)
    search_fields = ("file_name",)


@admin.register(BidPackage)
class BidPackageAdmin(admin.ModelAdmin):
    list_display = ("tender", "supplier", "status", "issued_at")
    list_filter = ("status",)
    search_fields = ("tender__reference", "supplier__email")


@admin.register(TenderResponse)
class TenderResponseAdmin(admin.ModelAdmin):
    list_display = ("reference", "tender", "supplier", "status", "total", "weighted_score")
    list_filter = ("status",)
    search_fields = ("reference", "tender__reference")
    inlines = (BidLineItemInline,)


@admin.register(BidLineItem)
class BidLineItemAdmin(admin.ModelAdmin):
    list_display = ("response", "lot", "quantity", "unit_price", "line_total")


@admin.register(EvaluationCriterion)
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ("tender", "name", "category", "weight", "max_score")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(BidEvaluation)
class BidEvaluationAdmin(admin.ModelAdmin):
    list_display = ("response", "criterion", "evaluator", "score", "evaluated_at")
    list_filter = ("criterion",)
    search_fields = ("response__reference",)


@admin.register(ReverseAuction)
class ReverseAuctionAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "buyer", "status", "starts_at", "ends_at", "current_best_bid")
    list_filter = ("status",)
    search_fields = ("reference", "title")
    inlines = (AuctionBidInline,)


@admin.register(AuctionBid)
class AuctionBidAdmin(admin.ModelAdmin):
    list_display = ("auction", "bidder", "amount", "currency", "placed_at", "is_winning")
    list_filter = ("is_winning",)


@admin.register(SupplierInvitation)
class SupplierInvitationAdmin(admin.ModelAdmin):
    list_display = ("tender", "supplier", "invited_by", "status", "invited_at")
    list_filter = ("status",)
    search_fields = ("tender__reference", "supplier__email")
