from rest_framework import serializers

from . import services
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
    ReorderListItem,
    ReturnItem,
    ReturnRequest,
    Settlement,
    Shipment,
    ShipmentItem,
    TaxRate,
    VolumeDiscount,
)


class ModelSerializer(serializers.ModelSerializer)
    class Meta:
        fields = "__all__"


def _serializer(model, extra_read_only=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra_read_only

    Auto.__name__ = f"{model.__name__}Serializer"
        return Auto


TaxRateSerializer = _serializer(TaxRate)
CustomerPricingSerializer = _serializer(CustomerPricing)
VolumeDiscountSerializer = _serializer(VolumeDiscount)
CreditTermSerializer = _serializer(CreditTerm)
PurchasingLimitSerializer = _serializer(PurchasingLimit)
ContractSerializer = _serializer(CommerceContract, extra_read_only=("status",))


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ("id", "customer", "status", "subtotal", "total", "created_at", "updated_at")


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("id", "number", "customer", "status", "created_at", "updated_at")


PurchaseOrderSerializer = _serializer(PurchaseOrder, extra_read_only=("status",))
ApprovalSerializer = _serializer(Approval, extra_read_only=("status", "decided_at"))
InvoiceSerializer = _serializer(Invoice, extra_read_only=("status", "amount_paid", "issued_at"))
PaymentSerializer = _serializer(Payment)
RefundSerializer = _serializer(Refund)
CancellationSerializer = _serializer(Cancellation)


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReturnRequest
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DeliveryTrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTrackingEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)
    tracking_events = DeliveryTrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


RecurringOrderSerializer = _serializer(RecurringOrder)


class ReorderListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReorderListItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReorderListSerializer(serializers.ModelSerializer):
    items = ReorderListItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReorderList
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


CommissionSerializer = _serializer(Commission)
MarketplaceFeeSerializer = _serializer(MarketplaceFee)
SettlementSerializer = _serializer(Settlement)
PayoutSerializer = _serializer(Payout)
TransactionSerializer = _serializer(LedgerTransaction)


class CreateOrderFromCartSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField(required=False)
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        request = self.context["request"]
        cart_id = self.validated_data.get("cart_id")
        if cart_id:
            cart = Cart.objects.prefetch_related("items").get(pk=cart_id, customer=request.user)
        else:
            cart = services.get_or_create_current_cart(request.user)
        return services.create_order_from_cart(
            cart,
            actor=request.user,
            shipping_address=self.validated_data.get("shipping_address", ""),
            billing_address=self.validated_data.get("billing_address", ""),
            notes=self.validated_data.get("notes", ""),
        )


class OrderTransitionSerializer(serializers.Serializer):
    status = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CreateInvoiceSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def save(self, **kwargs):
        order = Order.objects.get(pk=self.validated_data["order_id"])
        return services.create_invoice(order
class RecordPaymentSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField(required=False, default="USD")
    method = serializers.CharField(required=False, default="wire")
    reference = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        invoice = Invoice.objects.get(pk=self.validated_data["invoice_id"])
        request = self.context.get("request")
        return services.record_payment(
            invoice,
            self.validated_data["amount"],
            currency=self.validated_data.get("currency", "USD"),
            method=self.validated_data.get("method", "wire"),
            reference=self.validated_data.get("reference", ""),
            recorded_by=getattr(request, "user", None),
        )


class RecordRefundSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)
    payment_id = serializers.IntegerField(required=False)

    def save(self, **kwargs):
        invoice = Invoice.objects.get(pk=self.validated_data["invoice_id"])
        payment = None
        if self.validated_data.get("payment_id"):
            payment = Payment.objects.get(pk=self.validated_data["payment_id"])
        request = self.context.get("request")
        return services.record_refund(
            invoice,
            self.validated_data["amount"],
            reason=self.validated_data.get("reason", ""),
            payment=payment,
            recorded_by=getattr(request, "user", None),
        )


class CreateShipmentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    carrier = serializers.CharField(required=False, allow_blank=True)
    tracking_number = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(required=False)

    def save(self, **kwargs):
        order = Order.objects.prefetch_related("items").get(pk=self.validated_data["order_id"])
        return services.create_shipment_for_order(
            order,
            carrier=self.validated_data.get("carrier", ""),
            tracking_number=self.validated_data.get("tracking_number", ""),
            items=self.validated_data.get("items"),
        )
