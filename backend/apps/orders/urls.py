from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("tax-rates", views.TaxRateViewSet)
router.register("customer-pricing", views.CustomerPricingViewSet)
router.register("volume-discounts", views.VolumeDiscountViewSet)
router.register("credit-terms", views.CreditTermViewSet)
router.register("purchasing-limits", views.PurchasingLimitViewSet)
router.register("contracts", views.ContractViewSet)
router.register("carts", views.CartViewSet, basename="cart")
router.register("cart-items", views.CartItemViewSet, basename="cart-item")
router.register("orders", views.OrderViewSet, basename="order")
router.register("order-items", views.OrderItemViewSet)
router.register("order-status-history", views.OrderStatusHistoryViewSet)
router.register("purchase-orders", views.PurchaseOrderViewSet)
router.register("approvals", views.ApprovalViewSet)
router.register("invoices", views.InvoiceViewSet)
router.register("payments", views.PaymentViewSet)
router.register("refunds", views.RefundViewSet)
router.register("cancellations", views.CancellationViewSet)
router.register("return-requests", views.ReturnRequestViewSet)
router.register("return-items", views.ReturnItemViewSet)
router.register("shipments", views.ShipmentViewSet)
router.register("shipment-items", views.ShipmentItemViewSet)
router.register("delivery-tracking", views.DeliveryTrackingEventViewSet)
router.register("recurring-orders", views.RecurringOrderViewSet)
router.register("reorder-lists", views.ReorderListViewSet)
router.register("reorder-list-items", views.ReorderListItemViewSet)
router.register("commissions", views.CommissionViewSet)
router.register("marketplace-fees", views.MarketplaceFeeViewSet)
router.register("settlements", views.SettlementViewSet)
router.register("payouts", views.PayoutViewSet)
router.register("transactions", views.TransactionViewSet)
router.register("blanket-orders", views.BlanketOrderViewSet, basename="blanket-order")
router.register("blanket-order-releases", views.BlanketOrderReleaseViewSet)
router.register("delivery-schedules", views.DeliveryScheduleViewSet, basename="delivery-schedule")
router.register("order-milestones", views.OrderMilestoneViewSet, basename="order-milestone")
router.register("backorders", views.BackorderViewSet, basename="backorder")
router.register("credit-memos", views.CreditMemoViewSet, basename="credit-memo")
router.register("order-holds", views.OrderHoldViewSet, basename="order-hold")
router.register("packing-slips", views.PackingSlipViewSet, basename="packing-slip")

urlpatterns = [
    path("", include(router.urls)),
]
