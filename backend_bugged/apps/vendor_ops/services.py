from django.core.exceptions import ValidationError
from django.db.models import Count, Sum

from .models import IncomingOrder, InventoryAdjustment, InventoryItem, VendorAccount, VendorDispute, VendorPayout, VendorRFQ


def vendor_for_user(user, vendor_id=None)
    qs = VendorAccount.objects.filter(team__user=user, team__is_active=True) | VendorAccount.objects.filter(owner=user)
    qs = qs.distinct()
    if vendor_id:
        qs = qs.filter(pk=vendor_id)
    vendor = qs.first()
    if vendor is None:
        raise ValidationError("No vendor account is associated with this user.")
    return vendor


def incoming_work_dashboard(vendor):
    orders = vendor.incoming_orders.exclude(status__in=(IncomingOrder.Status.SHIPPED, IncomingOrder.Status.CLOSED))
    rfqs = vendor.rfqs.exclude(status__in=(VendorRFQ.Status.LOST, VendorRFQ.Status.WON))
    return {
        "vendor_id": vendor.pk,
        "open_orders": orders.count(),
        "open_rfqs": rfqs.count(),
        "orders": list(orders.values("id", "order_number", "status", "total", "due_at")[:50]),
        "rfqs": list(rfqs.values("id", "rfq_reference", "title", "status", "due_at")[:50]),
    }


def inventory_dashboard(vendor):
    items = vendor.inventory_items.all()
    low = [item for item in items if item.available <= item.reorder_point]
    return {
        "vendor_id": vendor.pk,
        "sku_count": items.count(),
        "low_stock_count": len(low),
        "on_hand": items.aggregate(total=Sum("quantity_on_hand"))["total"] or 0,
        "low_stock": [
            {"id": item.pk, "sku": item.sku, "name": item.name, "available": item.available, "reorder_point": item.reorder_point}
            for item in low[:50]
        ],
    }


def payout_dashboard(vendor):
    pending = vendor.payouts.filter(status=VendorPayout.Status.PENDING)
    paid = vendor.payouts.filter(status=VendorPayout.Status.PAID)
    return {
        "vendor_id": vendor.pk,
        "pending_count": pending.count(),
        "pending_amount": str(pending.aggregate(total=Sum("amount"))["total"] or 0),
        "paid_amount": str(paid.aggregate(total=Sum("amount"))["total"] or 0),
        "payouts": list(vendor.payouts.values("id", "amount", "currency", "status", "reference")[:50]),
    }


def dispute_dashboard(vendor):
    open_disputes = vendor.disputes.exclude(status=VendorDispute.Status.RESOLVED)
    return {
        "vendor_id": vendor.pk,
        "open_count": open_disputes.count(),
        "open_amount": str(open_disputes.aggregate(total=Sum("amount"))["total"] or 0),
        "disputes": list(open_disputes.values("id", "order_number", "subject", "status", "amount")[:50]),
    }


def sales_analytics(vendor):
    shipped = vendor.incoming_orders.filter(status__in=(IncomingOrder.Status.SHIPPED, IncomingOrder.Status.CLOSED))
    by_status = vendor.incoming_orders.values("status").annotate(count=Count("id"), total=Sum("total"))
    return {
        "vendor_id": vendor.pk,
        "order_count": vendor.incoming_orders.count(),
        "shipped_count": shipped.count(),
        "shipped_revenue": str(shipped.aggregate(total=Sum("total"))["total"] or 0),
        "by_status": list(by_status),
    }


def adjust_inventory(item, delta, reason="", actor=None):
    new_qty = item.quantity_on_hand + int(delta)
    if new_qty < 0:
        raise ValidationError("Inventory cannot go negative.")
    item.quantity_on_hand = new_qty
    item.save(update_fields=["quantity_on_hand", "updated_at"])
    return InventoryAdjustment.objects.create(item=item, delta=delta, reason=reason, actor=actor
def acknowledge_order(order):
    if order.status != IncomingOrder.Status.NEW:
        raise ValidationError("Only new incoming orders can be acknowledged.")
    order.status = IncomingOrder.Status.ACKNOWLEDGED
    order.save(update_fields=["status", "updated_at"])
    return order
