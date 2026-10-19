from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from . import models, services


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="buyer", password="pass")

    def test_checkout_converts_cart_into_order(self):
        cart = models.Cart.objects.create(customer=self.user)
        models.CartItem.objects.create(
            cart=cart,
            sku="SKU-1",
            product_name="Thread",
            quantity=10,
            unit_price=Decimal("100.00"),
        )

        order = services.create_order_from_cart(cart, actor=self.user)

        self.assertEqual(order.status, models.Order.Status.PENDING_APPROVAL)
        self.assertEqual(order.subtotal, Decimal("1000.00"))
        self.assertEqual(order.total, Decimal("1000.00"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(cart.status, models.Cart.Status.CONVERTED)
        self.assertEqual(order.status_history.count(), 1)
        self.assertTrue(models.PurchaseOrder.objects.filter(order=order).exists())

    def test_payment_marks_invoice_paid(self):
        order = models.Order.objects.create(
            customer=self.user,
            number="ORD-TEST",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )
        invoice = services.create_invoice(order)

        payment = services.record_payment(invoice, Decimal("10.00"), method="card", reference="pi_123")

        self.assertEqual(payment.status, models.Payment.Status.CAPTURED)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, models.Invoice.Status.PAID)

    def test_invalid_order_transition_is_rejected(self):
        order = models.Order.objects.create(customer=self.user, number="ORD-TRANS")
        with self.assertRaises(Exception):
            services.transition_order(order, models.Order.Status.PAID)

    def test_blanket_order_release_tracks_fulfillment(self):
        blanket = models.BlanketOrder.objects.create(
            customer=self.user,
            number="BLK-TEST",
            title="Annual thread supply",
            total_quantity=Decimal("100.000"),
            status=models.BlanketOrder.Status.ACTIVE,
        )
        order = models.Order.objects.create(customer=self.user, number="ORD-REL")

        release = services.release_from_blanket_order(blanket, order, Decimal("40.000"))

        self.assertEqual(release.quantity, Decimal("40.000"))
        blanket.refresh_from_db()
        self.assertEqual(blanket.fulfilled_quantity, Decimal("40.000"))
        self.assertEqual(blanket.status, models.BlanketOrder.Status.ACTIVE)
