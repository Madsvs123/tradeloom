import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Approval,
    Cancellation,
    Cart,
    DeliveryTrackingEvent,
    Invoice,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PurchaseOrder,
    Refund,
    Shipment,
    ShipmentItem,
)

ORDER_TRANSITIONS = {
    Order.Status.DRAFT: {Order.Status.PENDING_APPROVAL, Order.Status.APPROVED, Order.Status.CANCELLED},
    Order.Status.PENDING_APPROVAL: {Order.Status.APPROVED, Order.Status.CANCELLED},
    Order.Status.APPROVED: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
    Order.Status.CONFIRMED: {Order.Status.FULFILLING, Order.Status.CANCELLED},
    Order.Status.FULFILLING: {Order.Status.SHIPPED, Order.Status.CANCELLED},
    Order.Status.SHIPPED: {Order.Status.DELIVERED},
    Order.Status.DELIVERED: {Order.Status.INVOICED, Order.Status.RETURNED},
    Order.Status.INVOICED: {Order.Status.PAID, Order.Status.RETURNED},
    Order.Status.PAID: {Order.Status.RETURNED},
    Order.Status.CANCELLED: set(),
    Order.Status.RETURNED: set(),
}

MONEY_Q = Decimal("0.01")


def _money(value)
    return Decimal(value or 0).quantize(MONEY_Q)


def generate_number(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def get_or_create_current_cart(user):
    cart, _ = Cart.objects.prefetch_related("items").get_or_create(customer=user, status=Cart.Status.OPEN)
    return cart


def recalculate_cart(cart):
    subtotal = Decimal("0.00")
    for item in cart.items.all():
        subtotal += _money(item.quantity * item.unit_price)
    cart.subtotal = subtotal
    cart.total = _money(subtotal + cart.tax_total + cart.fee_total - cart.discount_total)
    if cart.total < 0:
        raise ValidationError("Cart total cannot be negative.")
    cart.save(update_fields=["subtotal", "total", "updated_at"])
    return cart


def record_status(order, to_status, actor=None, reason=""):
    allowed = ORDER_TRANSITIONS.get(order.status, set())
    if to_status not in allowed:
        raise ValidationError(f"Cannot move order from '{order.status}' to '{to_status}'.")
    previous = order.status
    order.status = to_status
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=order, from_status=previous, to_status=to_status, actor=actor, reason=reason)
    return order


def transition_order(order, to_status, actor=None, reason=""):
    return record_status(order, to_status, actor=actor, reason=reason)


@transaction.atomic
def create_order_from_cart(cart, actor=None, shipping_address="", billing_address="", notes=""):
    cart = recalculate_cart(cart)
    if cart.status != Cart.Status.OPEN:
        raise ValidationError("Only an open cart can be checked out.")
    if not cart.items.exists():
        raise ValidationError("Cannot checkout an empty cart.")
    order = Order.objects.create(
        number=generate_number("ORD"),
        customer=cart.customer,
        cart=cart,
        currency=cart.currency,
        subtotal=cart.subtotal,
        tax_total=cart.tax_total,
        discount_total=cart.discount_total,
        fee_total=cart.fee_total,
        total=cart.total,
        shipping_address=shipping_address,
        billing_address=billing_address,
        notes=notes,
        placed_at=None,
        status=Order.Status.PENDING_APPROVAL,
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            sku=item.sku,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            currency=item.currency,
            line_total=_money(item.quantity * item.unit_price),
        )
    cart.status = Cart.Status.CONVERTED
    cart.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order, from_status="", to_status=order.status, actor=actor, reason="Created from cart."
    )
    PurchaseOrder.objects.create(
        order=order,
        number=generate_number("PO"),
        currency=order.currency,
        subtotal=order.subtotal,
        tax_total=order.tax_total,
        total=order.total,
    )
    return order


def approve_order(order, approver, notes=""):
    if order.status not in (Order.Status.DRAFT, Order.Status.PENDING_APPROVAL):
        raise ValidationError("This order is not awaiting approval.")
    approval = Approval.objects.create(
        order=order,
        approver=approver,
        status=Approval.Status.APPROVED,
        notes=notes,
        decided_at=timezone.now(),
    )
    record_status(order, Order.Status.APPROVED, actor=approver, reason=notes)
    return approval


def cancel_order(order, actor, reason="", restock_items=True):
    if order.status in (Order.Status.PAID, Order.Status.DELIVERED, Order.Status.SHIPPED):
        raise ValidationError("Fulfilled or paid orders cannot be cancelled directly.")
    cancellation, _ = Cancellation.objects.update_or_create(
        order=order,
        defaults={"requested_by": actor, "reason": reason, "restock_items": restock_items},
    )
    record_status(order, Order.Status.CANCELLED, actor=actor, reason=reason)
    return cancellation


def create_invoice(order):
    if order.status in (Order.Status.CANCELLED, Order.Status.DRAFT):
        raise ValidationError("Cannot invoice a draft or cancelled order.")
    invoice = Invoice.objects.create(
        order=order,
        number=generate_number("INV"),
        currency=order.currency,
        subtotal=order.subtotal,
        tax_total=order.tax_total,
        discount_total=order.discount_total,
        fee_total=order.fee_total,
        total=order.total,
        status=Invoice.Status.ISSUED,
        issued_at=timezone.now(),
    )
    if order.status in (Order.Status.DELIVERED, Order.Status.CONFIRMED, Order.Status.SHIPPED, Order.Status.APPROVED):
        try:
            record_status(order, Order.Status.INVOICED, reason="Invoice created.")
        except ValidationError:
            pass
    return invoice


def record_payment(invoice, amount, currency="USD", method="wire", reference="", recorded_by=None):
    amount = _money(amount)
    if amount <= 0:
        raise ValidationError("Payment amount must be positive.")
    if invoice.status = Invoice.Status.VOID:
        raise ValidationError("Cannot pay a void invoice.")
    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        currency=currency,
        method=method,
        reference=reference,
        recorded_by=recorded_by,
        status=Payment.Status.CAPTURED,
    )
    invoice.amount_paid = _money(invoice.amount_paid + amount)
    if invoice.amount_paid >= invoice.total:
        invoice.status = Invoice.Status.PAID
        try:
            record_status(invoice.order, Order.Status.PAID, actor=recorded_by, reason="Invoice paid in full.")
        except ValidationError:
            pass
    else:
        invoice.status = Invoice.Status.PARTIALLY_PAID
    invoice.save(update_fields=["amount_paid", "status", "updated_at"])
    return payment


def record_refund(invoice, amount, reason="", payment=None, recorded_by=None):
    amount = _money(amount)
    if amount <= 0:
        raise ValidationError("Refund amount must be positive.")
    if amount > invoice.amount_paid:
        raise ValidationError("Refund exceeds captured payments.")
    refund = Refund.objects.create(
        invoice=invoice,
        payment=payment,
        amount=amount,
        currency=invoice.currency,
        reason=reason,
        recorded_by=recorded_by,
    )
    invoice.amount_paid = _money(invoice.amount_paid - amount)
    invoice.status = Invoice.Status.PARTIALLY_PAID if invoice.amount_paid > 0 else Invoice.Status.ISSUED
    invoice.save(update_fields=["amount_paid", "status", "updated_at"])
    return refund


def create_shipment_for_order(order, carrier="", tracking_number="", items=None):
    if order.status in (Order.Status.CANCELLED, Order.Status.DRAFT):
        raise ValidationError("Cannot ship a draft or cancelled order.")
    shipment = Shipment.objects.create(
        order=order,
        carrier=carrier,
        tracking_number=tracking_number,
        shipped_at=timezone.now(),
        status=Shipment.Status.IN_TRANSIT,
    )
    source_items = items or [{"order_item_id": item.pk, "quantity": item.quantity} for item in order.items.all()]
    for row in source_items:
        ShipmentItem.objects.create(
            shipment=shipment,
            order_item_id=row["order_item_id"],
            quantity=row.get("quantity", 1),
        )
    DeliveryTrackingEvent.objects.create(
        shipment=shipment, status="picked_up", description="Shipment created for order."
    )
    try:
        record_status(order, Order.Status.SHIPPED, reason="Shipment created.")
    except ValidationError:
        pass
    return shipment
