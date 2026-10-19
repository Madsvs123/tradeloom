from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framewrk.exceptions import PermissionDenied, ValidatonError

from .models import (
    IncomingOrder,
    InventoryAdjustment,
    InventoryItem,
    PriceBookChange,
    PriceBookItem,
    VendorAccount,
    VendorReport,
    VendorTeamMembership,

from .services import (
    apply_inventory_adjustment,
    apply_price_book_change,
    assert_vendor_permission,
    generate_report,
    incoming_work_dashboard,
    sales_analytics,
)


class VendorOpsServiceTests(TestCase)
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="test")
        self.analyst = User.objects.create_user(username="analyst", email="analyst@example.com", password="test")
        self.vendor = VendorAccount.objects.create(name="Acme Textiles", slug="acme-textiles")
        VendorTeamMembership.objects.create(vendor=self.vendor, user=self.owner, role=VendorTeamMembership.ROLE_OWNER)
        VendorTeamMembership.objects.create(vendor=self.vendor, user=self.analyst, role=VendorTeamMembership.ROLE_ANALYST)

    def test_team_permission_checks_role_capabilities(self):
        assert_vendor_permission(self.owner, self.vendor, "manage_inventory")
        with self.assertRaises(PermissionDenied):
            assert_vendor_permission(self.analyst, self.vendor, "manage_inventory")

    def test_inventory_adjustment_updates_stock_atomically(self):
        item = InventoryItem.objects.create(vendor=self.vendor, sku="LIN-001", title="Linen roll", quantity_on_hand=10)
        adjustment = InventoryAdjustment(vendor=self.vendor, item=item, delta=5, reason=InventoryAdjustment.REASON_RECOUNT)

        apply_inventory_adjustment(adjustment, self.owner)

        item.refresh_from_db()
        self.assertEqual(item.quantity_on_hand, 15)
        self.assertEqual(adjustment.adjusted_by, self.owner)

    def test_inventory_adjustment_rejects_reserved_stock_underflow(self):
        item = InventoryItem.objects.create(vendor=self.vendor, sku="LIN-002", title="Reserved linen", quantity_on_hand=10, reserved_quantity=7)
        adjustment = InventoryAdjustment(vendor=self.vendor, item=item, delta=-4)

        with self.assertRaises(ValidationError):
            apply_inventory_adjustment(adjustment, self.owner)

    def test_price_book_change_records_old_price_and_updates_item(self):
        price_item = PriceBookItem.objects.create(vendor=self.vendor, sku="LIN-001", title="Linen roll", unit_price=Decimal("12.00"))
        change = PriceBookChange(vendor=self.vendor, price_item=price_item, new_price=Decimal("14.50"), reason="Supplier increase")

        apply_price_book_change(change, self.owner)

        price_item.refresh_from_db()
        self.assertEqual(price_item.unit_price, Decimal("14.50"))
        self.assertEqual(change.old_price, Decimal("12.00"))

    def test_incoming_dashboard_counts_orders(self):
        IncomingOrder.objects.create(vendor=self.vendor, external_order_id="O-1", customer_name="Buyer One", subtotal=Decimal("100.00"))
        IncomingOrder.objects.create(
            vendor=self.vendor,
            external_order_id="O-2",
            customer_name="Buyer Two",
            status=IncomingOrder.STATUS_FULFILLED,
            subtotal=Decimal("50.00"),
        )

        dashboard = incoming_work_dashboard(self.vendor, self.owner)

        self.assertEqual(dashboard["orders"]["total"], 2)
        self.assertEqual(dashboard["orders"]["new"], 1)
        self.assertEqual(dashboard["orders"]["fulfilled"], 1)

    def test_sales_report_generation_persists_payload(self):
        IncomingOrder.objects.create(vendor=self.vendor, external_order_id="O-3", customer_name="Buyer", subtotal=Decimal("75.00"))

        analytics = sales_analytics(self.vendor, self.analyst, days=30)
        report = generate_report(self.vendor, VendorReport.TYPE_SALES, {"days": 30}, self.analyst)

        self.assertEqual(analytics["totals"]["orders"], 1)
        self.assertEqual(report.status, VendorReport.STATUS_READY)
        self.assertEqual(report.generated_payload["totals"]["orders"], 1)
