from django.contrib import admin

from .models import (
    Approval,
    Backorder,
    BlanketOrder,
    BlanketOrderRelease,
    Cancellation,
    Cart,
    CartItem,
    CommerceContract,
    Commission,
    CreditMemo,
    CreditTerm,
    CustomerPricing,
    DeliverySchedule,
    DeliveryTrackingEvent,
    Invoice,
    LedgerTransaction,
    MarketplaceFee,
    Order,
    OrderHold,
    OrderItem,
    OrderMilestone,
    OrderStatusHistory,
    PackingSlip,
    Payment,
    Payout,
    PurchaseOrder,
    PurchasingLimit,
    RecurringOrder,
    Refund,
    ReorderList,
    ReorderListItem,
    ReturnItem,
    ReturnRequest,
    Settlement,
    Shipment,
    ShipmentItem,
    TaxRate,
    VolumeDiscount,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "total", "currency", "placed_at")
    list_filter = ("status",)
    search_fields = ("number", "customer__email")
    inlines = (OrderItemInline,)


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("name", "jurisdiction", "percent", "is_active")
    list_filter = ("is_active",)


@admin.register(CustomerPricing)
class CustomerPricingAdmin(admin.ModelAdmin):
    list_display = ("customer", "sku", "unit_price", "currency", "is_active")
    list_filter = ("is_active",)


@admin.register(VolumeDiscount)
class VolumeDiscountAdmin(admin.ModelAdmin):
    list_display = ("sku", "customer", "min_quantity", "percent_off", "is_active")
    list_filter = ("is_active",)


@admin.register(CreditTerm)
class CreditTermAdmin(admin.ModelAdmin):
    list_display = ("customer", "net_days", "credit_limit", "currency", "is_active")


@admin.register(PurchasingLimit)
class PurchasingLimitAdmin(admin.ModelAdmin):
    list_display = ("customer", "sku", "period", "max_amount", "is_active")
    list_filter = ("period", "is_active")


@admin.register(CommerceContract)
class CommerceContractAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "total", "starts_at", "ends_at")
    list_filter = ("status",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = (CartItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "sku", "product_name", "quantity", "line_total")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "from_status", "to_status", "actor", "created_at")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "order", "status", "total")
    list_filter = ("status",)


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("order", "approver", "status", "decided_at")
    list_filter = ("status",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "order", "status", "total", "amount_paid", "due_date")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "method", "status", "refrence")
    list_filter = ("status", "method")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "reason")


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("order", "requested_by", "restock_items")


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "requested_by")
    list_filter = ("status",)


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ("return_request", "order_item", "quantity")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "tracking_number", "status", "shipped_at")
    list_filter = ("status",)


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ("shipment", "order_item", "quantity")


@admin.register(DeliveryTrackingEvent)
class DeliveryTrackingEventAdmin(admin.ModelAdmin):
    list_display = ("shipment", "status", "location", "occurred_at")


@admin.register(RecurringOrder)
class RecurringOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "interval_days", "next_run_at", "status")
    list_filter = ("status",)


@admin.register(ReorderList)
class ReorderListAdmin(admin.ModelAdmin):
    list_display = ("name", "customer")


@admin.register(ReorderListItem)
class ReorderListItemAdmin(admin.ModelAdmin):
    list_display = ("reorder_list", "sku", "quantity")


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("order", "vendor_id", "rate", "amount")


@admin.register(MarketplaceFee)
class MarketplaceFeeAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "amount")


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "amount", "settled_at")
    list_filter = ("status",)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("settlement", "amount", "status", "destination")
    list_filter = ("status",)


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(admin.ModelAdmin):
    list_display = ("order", "kind", "amount", "reference")


@admin.register(BlanketOrder)
class BlanketOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "total_quantity", "fulfilled_quantity", "starts_at", "ends_at")
    list_filter = ("status",)
    search_fields = ("number", "title", "customer__email")


@admin.register(BlanketOrderRelease)
class BlanketOrderReleaseAdmin(admin.ModelAdmin):
    list_display = ("blanket_order", "order", "quantity", "released_at")


@admin.register(DeliverySchedule)
class DeliveryScheduleAdmin(admin.ModelAdmin):
    list_display = ("order", "sequence", "scheduled_date", "quantity", "status")
    list_filter = ("status",)


@admin.register(OrderMilestone)
class OrderMilestoneAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "due_at", "status")
    list_filter = ("status",)


@admin.register(Backorder)
class BackorderAdmin(admin.ModelAdmin):
    list_display = ("order", "order_item", "quantity", "fulfilled_quantity", "status")
    list_filter = ("status",)


@admin.register(CreditMemo)
class CreditMemoAdmin(admin.ModelAdmin):
    list_display = ("number", "order", "invoice", "status", "total")
    list_filter = ("status",)


@admin.register(OrderHold)
class OrderHoldAdmin(admin.ModelAdmin):
    list_display = ("order", "reason", "status", "placed_by", "released_by", "released_at")
    list_filter = ("reason", "status")


@admin.register(PackingSlip)
class PackingSlipAdmin(admin.ModelAdmin):
    list_display = ("number", "shipment", "generated_by", "created_at")
