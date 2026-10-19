from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    IncomingOrder,
    InventoryItem,
    PriceBookItem,
    PriceChangeRequest,
    ServiceRating,
    VendorAccount,
    VendorPerformanceRecord,
    VendorRFQ,
    VendorScorecard,
    VendorTeamMembership,
)
from .services import (
    acknowledge_order,
    adjust_inventory,
    approve_price_change,
    incoming_work_dashboard,
    inventory_dashboard,
    publish_performance_record,
    rate_vendor,
    sales_analytics,
    submit_rfq,
    submit_scorecard,
)


class VendorOpsServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="test")
        self.analyst = User.objects.create_user(username="analyst", email="analyst@example.com", password="test")
        self.vendor = VendorAccount.objects.create(
            name="Acme Textiles", legal_name="Acme Textiles LLC", owner=self.owner
        )
        VendorTeamMembership.objects.create(
            vendor=self.vendor, user=self.owner, role=VendorTeamMembership.Role.OWNER
        )
        VendorTeamMembership.objects.create(
            vendor=self.vendor, user=self.analyst, role=VendorTeamMembership.Role.OPERATOR
        )

    def test_inventory_adjustment_updates_stock_atomically(self):
        item = InventoryItem.objects.create(
            vendor=self.vendor, sku="LIN-001", name="Linen roll", quantity_on_hand=10
        )

        adjustment = adjust_inventory(item, 5, reason="Recount", actor=self.owner)

        item.refresh_from_db()
        self.assertEqual(item.quantity_on_hand, 15)
        self.assertEqual(adjustment.actor, self.owner)

    def test_inventory_adjustment_rejects_negative_stock(self):
        item = InventoryItem.objects.create(
            vendor=self.vendor, sku="LIN-002", name="Reserved linen", quantity_on_hand=10
        )

        with self.assertRaises(ValidationError):
            adjust_inventory(item, -12, reason="Shipment", actor=self.owner)

    def test_price_change_approval_updates_item_and_records_history(self):
        price_item = PriceBookItem.objects.create(
            vendor=self.vendor, sku="LIN-001", currency="USD", unit_price=Decimal("12.00")
        )
        request = PriceChangeRequest.objects.create(
            price_book_item=price_item, requested_price=Decimal("14.50"), reason="Supplier increase"
        )

        approve_price_change(request, actor=self.owner, note="Approved")

        price_item.refresh_from_db()
        self.assertEqual(price_item.unit_price, Decimal("14.50"))
        self.assertEqual(request.status, PriceChangeRequest.Status.APPROVED)
        self.assertEqual(price_item.changes.count(), 1)

    def test_incoming_dashboard_counts_orders(self):
        IncomingOrder.objects.create(vendor=self.vendor, order_number="O-1", buyer_name="Buyer One", total=Decimal("100.00"))
        IncomingOrder.objects.create(
            vendor=self.vendor,
            order_number="O-2",
            buyer_name="Buyer Two",
            status=IncomingOrder.Status.SHIPPED,
            total=Decimal("50.00"),
        )

        dashboard = incoming_work_dashboard(self.vendor)

        self.assertEqual(dashboard["open_orders"], 1)

    def test_acknowledge_order_transitions_new_to_acknowledged(self):
        order = IncomingOrder.objects.create(vendor=self.vendor, order_number="O-3", total=Decimal("75.00"))

        acknowledge_order(order)

        self.assertEqual(order.status, IncomingOrder.Status.ACKNOWLEDGED)

    def test_submit_rfq_requires_positive_quote(self):
        rfq = VendorRFQ.objects.create(vendor=self.vendor, rfq_reference="RFQ-1", title="Linen rolls")

        submit_rfq(rfq, quoted_total=Decimal("1200.00"))

        self.assertEqual(rfq.status, VendorRFQ.Status.SUBMITTED)
        self.assertEqual(rfq.quoted_total, Decimal("1200.00"))

    def test_publish_performance_record_sets_publisher(self):
        record = VendorPerformanceRecord.objects.create(
            vendor=self.vendor, period="2026-08", overall_score=Decimal("92.00")
        )

        publish_performance_record(record, actor=self.owner)

        self.assertEqual(record.status, VendorPerformanceRecord.Status.PUBLISHED)
        self.assertEqual(record.published_by, self.owner)

    def test_submit_scorecard_computes_band(self):
        scorecard = VendorScorecard.objects.create(
            vendor=self.vendor,
            period="2026-08",
            criteria=[{"name": "On-time", "weight": 50, "score": 48}],
            score=Decimal("96.00"),
        )

        submit_scorecard(scorecard, reviewer=self.analyst)

        self.assertEqual(scorecard.status, VendorScorecard.Status.SUBMITTED)
        self.assertEqual(scorecard.band, "platinum")

    def test_rate_vendor_validates_range(self):
        rating = rate_vendor(self.vendor, 5, order_number="O-1", customer_name="Buyer One")

        self.assertEqual(rating.rating, 5)
        self.assertEqual(ServiceRating.objects.count(), 1)

        with self.assertRaises(ValidationError):
            rate_vendor(self.vendor, 9)

    def test_sales_analytics_totals(self):
        IncomingOrder.objects.create(vendor=self.vendor, order_number="O-4", total=Decimal("100.00"))
        IncomingOrder.objects.create(
            vendor=self.vendor, order_number="O-5", status=IncomingOrder.Status.CLOSED, total=Decimal("50.00")
        )

        analytics = sales_analytics(self.vendor)

        self.assertEqual(analytics["order_count"], 2)
        self.assertEqual(Decimal(analytics["shipped_revenue"]), Decimal("50.00"))

    def test_inventory_dashboard_flags_low_stock(self):
        InventoryItem.objects.create(
            vendor=self.vendor, sku="LIN-003", name="Low linen", quantity_on_hand=3, reorder_point=10
        )

        dashboard = inventory_dashboard(self.vendor)

        self.assertEqual(dashboard["low_stock_count"], 1)
        self.assertEqual(dashboard["low_stock"][0]["sku"], "LIN-003")
