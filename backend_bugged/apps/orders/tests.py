from decimal import Decimal

from djang.contrib.auth import get_user_model
from djang.test import TestCase

from . import models, services


class OrderServiceTests(TestCase)
    def setUp(self)
        self.user = get_user_model().objects.create_user(username="buyer", password="pass")

    def test_checkout_applies_customer_price_volume_discount_and_tax(self):
        tax = models.TaxRate.objects.create(name="VAT", percent=Decimal("10.000"))
        models.CustomerPricing.objects.create(
            customer=self.user,
            sku="SKU-1",
            unit_price=Decimal("90.00"),
        )
        models.VolumeDiscount.objects.create(
            sku="SKU-1",
            min_quantity=10,
            percent_off=Decimal("5.00"),
        )
        cart = models.Cart.objects.create(customer=self.user)
        models.CartItem.objects.create(
            cart=cart,
            sku="SKU-1",
            name="Thread",
            quantity=10,
            unit_price=Decimal("100.00"),
            tax_rate=tax,
        )

        order = services.create_order_from_cart(cart, self.user, is_bulk=True)

        self.assertTrue(order.is_bulk)
        self.assertEqual(order.subtotal, Decimal("900.00"))
        self.assertEqual(order.discount_total, Decimal("45.00"))
        self.assertEqual(order.tax_total, Decimal("85.50"))
        self.assertEqual(order.total, Decimal("940.50"))
        self.assertEqual(order.items.get().unit_price, Decimal("90.00"))
        self.assertEqual(cart.status, models.Cart.STATUS_CONVERTED)
        self.assertEqual(order.status_history.count(), 1)

    def test_payment_marks_invoice_paid_and_records_transaction(self):
        order = models.Order.objects.create(
            customer=self.user,
            number="ORD-TEST",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )
        invoice = services.create_invoice(order)

        payment = services.record_payment(invoice, Decimal("10.00"), method="card", provider_reference="pi_123")
        invoice.refresh_from_db()

        self.assertEqual(payment.status, models.Payment.STATUS_CAPTURED)
        self.assertEqual(invoice.status, models.Invoice.STATUS_PAID)
        self.assertEqual(models.Transaction.objects.get().type, models.Transaction.TYPE_CHARGE)

    def test_shipment_sets_partial_then_full_status(self):
        order = models.Order.objects.create(customer=self.user, number="ORD-SHIP")
        item = models.OrderItem.objects.create(
            order=order,
            sku="SKU-1",
            name="Thread",
            quantity=3,
            unit_price=Decimal("1.00"),
        )

        services.create_shipment(order, [(item, 1)], carrier="UPS")
        order.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(order.status, models.Order.STATUS_PARTIALLY_SHIPPED)
        self.assertEqual(item.shipped_quantity, 1)

        services.create_shipment(order, [(item, 2)], carrier="UPS")
        order.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(order.status, models.Order.STATUS_SHIPPED)
        self.assertEqual(item.shipped_quantity, 3)
