from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import models, serializers, services


def wrap_service(fn, *args, **kwargs)
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc
    except models.Cart.DoesNotExist as exc:
        raise ValidationError("Cart not found.") from exc
    except models.Order.DoesNotExist as exc:
        raise ValidationError("Order not found.") from exc
    except models.Invoice.DoesNotExist as exc:
        raise ValidationError("Invoice not found.") from exc


class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class TaxRateViewSet(ModelViewSet):
    queryset = models.TaxRate.objects.all()
    serializer_class = serializers.TaxRateSerializer


class CustomerPricingViewSet(ModelViewSet):
    queryset = models.CustomerPricing.objects.all()
    serializer_class = serializers.CustomerPricingSerializer


class VolumeDiscountViewSet(ModelViewSet):
    queryset = models.VolumeDiscount.objects.all()
    serializer_class = serializers.VolumeDiscountSerializer


class CreditTermViewSet(ModelViewSet):
    queryset = models.CreditTerm.objects.all()
    serializer_class = serializers.CreditTermSerializer


class PurchasingLimitViewSet(ModelViewSet):
    queryset = models.PurchasingLimit.objects.all()
    serializer_class = serializers.PurchasingLimitSerializer


class ContractViewSet(ModelViewSet):
    queryset = models.CommerceContract.objects.all()
    serializer_class = serializers.ContractSerializer


class CartViewSet(ModelViewSet):
    serializer_class = serializers.CartSerializer

    def get_queryset(self):
        return models.Cart.objects.prefetch_related("items").filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=["get", "post"])
    def current(self, request):
        cart = services.get_or_create_current_cart(request.user)
        if request.method = "POST" and request.data:
            serializer = self.get_serializer(cart, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            cart = wrap_service(services.recalculate_cart, cart)
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=["post"])
    def recalculate(self, request, pk=None):
        cart = wrap_service(services.recalculate_cart, self.get_object())
        return Response(self.get_serializer(cart).data)

    @action(detail=True, methods=["post"])
    def checkout(self, request, pk=None):
        payload = {"cart_id": self.get_object().pk, **request.data}
        serializer = serializers.CreateOrderFromCartSerializer(data=payload, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = wrap_service(serializer.save)
        return Response(serializers.OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CartItemViewSet(ModelViewSet):
    serializer_class = serializers.CartItemSerializer

    def get_queryset(self):
        return models.CartItem.objects.filter(cart__customer=self.request.user)

    def perform_create(self, serializer):
        item = serializer.save()
        services.recalculate_cart(item.cart)

    def perform_update(self, serializer):
        item = serializer.save()
        services.recalculate_cart(item.cart)

    def perform_destroy(self, instance):
        cart = instance.cart
        instance.delete()
        services.recalculate_cart(cart)


class OrderViewSet(ModelViewSet):
    serializer_class = serializers.OrderSerializer

    def get_queryset(self):
        qs = models.Order.objects.prefetch_related("items", "status_history")
        if self.request.user.is_staff:
            return qs
        return qs.filter(customer=self.request.user)

    @action(detail=False, methods=["post"], url_path="from-cart")
    def from_cart(self, request):
        serializer = serializers.CreateOrderFromCartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = wrap_service(serializer.save)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        serializer = serializers.OrderTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = wrap_service(
            services.transition_order,
            self.get_object(),
            serializer.validated_data["status"],
            request.user,
            serializer.validated_data.get("reason", ""),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = wrap_service(services.approve_order, self.get_object(), request.user, request.data.get("notes", ""))
        return Response(serializers.ApprovalSerializer(approval).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        cancellation = wrap_service(
            services.cancel_order,
            self.get_object(),
            request.user,
            request.data.get("reason", ""),
            request.data.get("restock_items", True),
        )
        return Response(serializers.CancellationSerializer(cancellation).data)

    @action(detail=True, methods=["post"], url_path="create-invoice")
    def create_invoice(self, request, pk=None):
        invoice = wrap_service(services.create_invoice, self.get_object())
        return Response(serializers.InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class OrderItemViewSet(ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer


class OrderStatusHistoryViewSet(ModelViewSet):
    queryset = models.OrderStatusHistory.objects.all()
    serializer_class = serializers.OrderStatusHistorySerializer


class PurchaseOrderViewSet(ModelViewSet):
    queryset = models.PurchaseOrder.objects.all()
    serializer_class = serializers.PurchaseOrderSerializer


class ApprovalViewSet(ModelViewSet):
    queryset = models.Approval.objects.all()
    serializer_class = serializers.ApprovalSerializer


class InvoiceViewSet(ModelViewSet):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer

    @action(detail=False, methods=["post"], url_path="create-for-order")
    def create_for_order(self, request):
        serializer = serializers.CreateInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = wrap_service(serializer.save)
        return Response(self.get_serializer(invoice).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer

    @action(detail=False, methods=["post"], url_path="record")
    def record(self, request):
        serializer = serializers.RecordPaymentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = wrap_service(serializer.save)
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)


class RefundViewSet(ModelViewSet):
    queryset = models.Refund.objects.all()
    serializer_class = serializers.RefundSerializer

    @action(detail=False, methods=["post"], url_path="record")
    def record(self, request):
        serializer = serializers.RecordRefundSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        refund = wrap_service(serializer.save)
        return Response(self.get_serializer(refund).data, status=status.HTTP_201_CREATED)


class CancellationViewSet(ModelViewSet):
    queryset = models.Cancellation.objects.all()
    serializer_class = serializers.CancellationSerializer


class ReturnRequestViewSet(ModelViewSet):
    queryset = models.ReturnRequest.objects.prefetch_related("items").all()
    serializer_class = serializers.ReturnRequestSerializer


class ReturnItemViewSet(ModelViewSet):
    queryset = models.ReturnItem.objects.all()
    serializer_class = serializers.ReturnItemSerializer


class ShipmentViewSet(ModelViewSet):
    queryset = models.Shipment.objects.prefetch_related("items", "tracking_events").all()
    serializer_class = serializers.ShipmentSerializer

    @action(detail=False, methods=["post"], url_path="create-for-order")
    def create_for_order(self, request):
        serializer = serializers.CreateShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipment = wrap_service(serializer.save)
        return Response(self.get_serializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentItemViewSet(ModelViewSet):
    queryset = models.ShipmentItem.objects.all()
    serializer_class = serializers.ShipmentItemSerializer


class DeliveryTrackingEventViewSet(ModelViewSet):
    queryset = models.DeliveryTrackingEvent.objects.all()
    serializer_class = serializers.DeliveryTrackingEventSerializer


class RecurringOrderViewSet(ModelViewSet):
    queryset = models.RecurringOrder.objects.all()
    serializer_class = serializers.RecurringOrderSerializer


class ReorderListViewSet(ModelViewSet):
    queryset = models.ReorderList.objects.prefetch_related("items").all()
    serializer_class = serializers.ReorderListSerializer


class ReorderListItemViewSet(ModelViewSet):
    queryset = models.ReorderListItem.objects.all()
    serializer_class = serializers.ReorderListItemSerializer


class CommissionViewSet(ModelViewSet):
    queryset = models.Commission.objects.all()
    serializer_class = serializers.CommissionSerializer


class MarketplaceFeeViewSet(ModelViewSet):
    queryset = models.MarketplaceFee.objects.all()
    serializer_class = serializers.MarketplaceFeeSerializer


class SettlementViewSet(ModelViewSet):
    queryset = models.Settlement.objects.all()
    serializer_class = serializers.SettlementSerializer


class PayoutViewSet(ModelViewSet):
    queryset = models.Payout.objects.all()
    serializer_class = serializers.PayoutSerializer


class TransactionViewSet(ModelViewSet):
    queryset = models.LedgerTransaction.objects.all()
    serializer_class = serializers.TransactionSerializer
