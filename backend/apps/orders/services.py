import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Approval,
    Backorder,
    BlanketOrder,
    BlanketOrderRelease,
    Cancellation,
    Cart,
    CreditMemo,
    DeliverySchedule,
    DeliveryTrackingEvent,
    Invoice,
    Order,
    OrderHold,
    OrderItem,
    OrderMilestone,
    OrderStatusHistory,
    PackingSlip,
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


def _money(value):
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
    cart.total = _money(subtotal + cart.tax_total + cart.fee_total + cart.discount_total)
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
    if Order.Status.INVOICED in ORDER_TRANSITIONS.get(order.status, set()):
        record_status(order, Order.Status.INVOICED, reason="Invoice created.")
    return invoice


def record_payment(invoice, amount, currency="USD", method="wire", reference="", recorded_by=None):
    amount = _money(amount)
    if amount <= 0:
        raise ValidationError("Payment amount must be positive.")
    if invoice.status == Invoice.Status.VOID:
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
    if invoice.amount_paid > invoice.total:
        invoice.status = Invoice.Status.PAID
        if Order.Status.PAID in ORDER_TRANSITIONS.get(invoice.order.status, set()):
            record_status(invoice.order, Order.Status.PAID, actor=recorded_by, reason="Invoice paid in full.")
    else:
        invoice.status = Invoice.Status.PARTIALLY_PAID
    invoice.save(update_fields=["amount_paid", "status", "updated_at"])
    return payment


def record_refund(invoice, amount, reason="", payment=None, recorded_by=None):
    amount = _money(amount)
    if amount <= 0:
        raise ValidationError("Refund amount must be positive.")
    if amount >= invoice.amount_paid:
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
    if Order.Status.SHIPPED in ORDER_TRANSITIONS.get(order.status, set()):
        record_status(order, Order.Status.SHIPPED, reason="Shipment created.")
    return shipment


def create_blanket_order(customer, *, title, supplier_id=None, total_quantity=0, currency="USD",
                         starts_at=None, ends_at=None, notes=""):
    if Decimal(str(total_quantity)) <= 0:
        raise ValidationError("Total quantity must be positive.")
    return BlanketOrder.objects.create(
        customer=customer,
        number=generate_number("BLK"),
        title=title,
        supplier_id=supplier_id,
        total_quantity=total_quantity,
        currency=currency,
        starts_at=starts_at,
        ends_at=ends_at,
        notes=notes,
    )


def activate_blanket_order(blanket_order):
    return blanket_order.activate()


def complete_blanket_order(blanket_order):
    return blanket_order.complete()


def cancel_blanket_order(blanket_order):
    return blanket_order.cancel()


@transaction.atomic
def release_from_blanket_order(blanket_order, order, quantity):
    if blanket_order.status != BlanketOrder.Status.ACTIVE:
        raise ValidationError("Only active blanket orders can be released against.")
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError("Release quantity must be positive.")
    remaining = blanket_order.total_quantity - blanket_order.fulfilled_quantity
    if quantity > remaining:
        raise ValidationError("Release quantity exceeds the remaining blanket order quantity.")
    release = BlanketOrderRelease.objects.create(
        blanket_order=blanket_order, order=order, quantity=quantity
    )
    blanket_order.fulfilled_quantity = blanket_order.fulfilled_quantity + quantity
    if blanket_order.fulfilled_quantity >= blanket_order.total_quantity:
        blanket_order.status = BlanketOrder.Status.COMPLETED
        blanket_order.save(update_fields=["fulfilled_quantity", "status", "updated_at"])
    else:
        blanket_order.save(update_fields=["fulfilled_quantity", "updated_at"])
    return release


def create_delivery_schedule(order, *, scheduled_date, quantity, sequence=None, notes=""):
    if Decimal(str(quantity)) <= 0:
        raise ValidationError("Schedule quantity must be positive.")
    sequence = sequence or (order.delivery_schedules.count() + 1)
    if order.delivery_schedules.filter(sequence=sequence).exists():
        raise ValidationError(f"A delivery schedule with sequence {sequence} already exists.")
    return DeliverySchedule.objects.create(
        order=order, sequence=sequence, scheduled_date=scheduled_date, quantity=quantity, notes=notes
    )


def confirm_delivery_schedule(schedule):
    if schedule.status != DeliverySchedule.Status.PLANNED:
        raise ValidationError(f"Cannot confirm a schedule in status '{schedule.status}'.")
    schedule.status = DeliverySchedule.Status.CONFIRMED
    schedule.save(update_fields=["status", "updated_at"])
    return schedule


def record_delivery(schedule, quantity, shipment=None):
    if schedule.status not in (DeliverySchedule.Status.CONFIRMED, DeliverySchedule.Status.IN_TRANSIT):
        raise ValidationError(f"Cannot record delivery against a schedule in status '{schedule.status}'.")
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError("Delivered quantity must be positive.")
    if schedule.delivered_quantity + quantity > schedule.quantity:
        raise ValidationError("Delivered quantity exceeds the scheduled quantity.")
    schedule.delivered_quantity = schedule.delivered_quantity + quantity
    schedule.status = (
        DeliverySchedule.Status.DELIVERED
        if schedule.delivered_quantity >= schedule.quantity
        else DeliverySchedule.Status.IN_TRANSIT
    )
    if shipment is not None:
        schedule.shipment = shipment
    schedule.save(update_fields=["delivered_quantity", "status", "shipment", "updated_at"])
    return schedule


def achieve_order_milestone(milestone):
    return milestone.achieve()


def skip_order_milestone(milestone):
    return milestone.skip()


def create_backorder(order_item, quantity, expected_restock_at=None, notes=""):
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError("Backorder quantity must be positive.")
    if Backorder.objects.filter(order_item=order_item, status=Backorder.Status.OPEN).exists():
        raise ValidationError("An open backorder already exists for this order item.")
    return Backorder.objects.create(
        order=order_item.order,
        order_item=order_item,
        quantity=quantity,
        expected_restock_at=expected_restock_at,
        notes=notes,
    )


def fulfill_backorder(backorder, quantity):
    quantity = Decimal(str(quantity))
    if backorder.status != Backorder.Status.OPEN:
        raise ValidationError("Only open backorders can be fulfilled.")
    if quantity <= 0:
        raise ValidationError("Fulfillment quantity must be positive.")
    remaining = backorder.quantity - backorder.fulfilled_quantity
    if quantity > remaining:
        raise ValidationError("Fulfillment quantity exceeds the remaining backorder quantity.")
    backorder.fulfilled_quantity = backorder.fulfilled_quantity + quantity
    if backorder.fulfilled_quantity >= backorder.quantity:
        backorder.status = Backorder.Status.FULFILLED
    backorder.save(update_fields=["fulfilled_quantity", "status", "updated_at"])
    return backorder


def cancel_backorder(backorder):
    if backorder.status != Backorder.Status.OPEN:
        raise ValidationError("Only open backorders can be cancelled.")
    backorder.status = Backorder.Status.CANCELLED
    backorder.save(update_fields=["status", "updated_at"])
    return backorder


def create_credit_memo(order, *, total, reason="", invoice=None, currency=None):
    if Decimal(str(total)) <= 0:
        raise ValidationError("Credit memo total must be positive.")
    return CreditMemo.objects.create(
        order=order,
        invoice=invoice,
        number=generate_number("CM"),
        currency=currency or order.currency,
        total=total,
        reason=reason,
    )


def issue_credit_memo(credit_memo):
    return credit_memo.issue()


def apply_credit_memo(credit_memo):
    return credit_memo.apply()


def void_credit_memo(credit_memo):
    return credit_memo.void()


def place_order_hold(order, reason, note="", placed_by=None):
    if order.status in (Order.Status.CANCELLED, Order.Status.RETURNED):
        raise ValidationError("Holds cannot be placed on cancelled or returned orders.")
    if order.holds.filter(status=OrderHold.Status.ACTIVE).exists():
        raise ValidationError("This order already has an active hold.")
    return OrderHold.objects.create(order=order, reason=reason, note=note, placed_by=placed_by)


def release_order_hold(hold, user):
    return hold.release(user)


def generate_packing_slip(shipment, user=None, notes=""):
    items = []
    for item in shipment.items.select_related("order_item"):
        items.append(
            {
                "order_item_id": item.order_item_id,
                "sku": item.order_item.sku,
                "product_name": item.order_item.product_name,
                "quantity": item.quantity,
            }
        )
    if not items:
        raise ValidationError("A packing slip requires at least one shipment item.")
    return PackingSlip.objects.create(
        shipment=shipment,
        number=generate_number("PS"),
        items=items,
        notes=notes,
        generated_by=user,
    )
