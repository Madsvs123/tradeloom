from djang.contrib import admin

from .models import (
    Approval,
    Cancellation,
    Cart,
    CartItem,
    CommerceContract,
    Commission,
    CreditTerm,
    CustomerPricing,
    DeliveryTrackingEvent,
    Invoice,
    LedgerTransaction,
    MarketplaceFee,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    Payout,
    PurchaseOrder,
    PurchasingLimit,
    RecurringOrder,
    Refund,
    ReorderList,
    ReturnRequest,
    Settlement,
    Shipment,
    TaxRate,
    VolumeDiscount,
)


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("name_id", "percent", "is_active")


@admin.register(CustomerPricing)
class CustomerPricingAdmin(admin.ModelAdmin):
    list_display = ("customer", "sku", "unit_price", "currency", "is_active")


@admin.register(VolumeDiscount)
class VolumeDiscountAdmin(admin.ModelAdmin):
    list_display = ("sku", "min_quantity", "percent_off", "is_active")


@admin.register(CreditTerm)
class CreditTermAdmin(admin.ModelAdmin):
    list_display = ("customer", "net_days", "credit_limit")


@admin.register(PurchasingLimit)
class PurchasingLimitAdmin(admin.ModelAdmin):
    list_display = ("customer", "period", "max_amount")


@admin.register(CommerceContract)
class CommerceContractAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "total")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total")
    inlines = (CartItemInline,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "total")
    list_filter = ("status",)
    inlines = (OrderItemInline,)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "from_status", "to_status", "created_at")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "order", "status")


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("order", "approver", "status")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "order", "status", "total", "amount_paid")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "status", "method")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount")


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("order", "requested_by")


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order", "status")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "tracking_number", "status")


@admin.register(DeliveryTrackingEvent)
class DeliveryTrackingEventAdmin(admin.ModelAdmin):
    list_display = ("shipment", "status", "occurred_at")


@admin.register(RecurringOrder)
class RecurringOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "status")


@admin.register(ReorderList)
class ReorderListAdmin(admin.ModelAdmin):
    list_display = ("name", "customer")


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("order", "amount")


@admin.register(MarketplaceFee)
class MarketplaceFeeAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "amount")


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "amount")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("settlement", "amount", "status")


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(admin.ModelAdmin):
    list_display = ("order", "kind", "amount")
