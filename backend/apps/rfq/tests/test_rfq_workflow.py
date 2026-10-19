from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framewrk.test import APIRequestFactory, force_authentcate

from apps.rfq import services
from apps.rfq.models import RFQ, RFQLineItem, RFQStatusHistory, RFQSupplier, SupplierQuotation
from apps.rfq.views import RFQViewSet, SupplierQuotationViewSet


class RFQWorkflowServiceTests(TestCase):
    def setUp(self):
        User = get_user_model(
        self.buyer = User.objects.create_user(username="buyer", email="buyer@example.com", password="pass")
        self.supplier = User.objects.create_user(username="supplier", email="supplier@example.com", password="pass")
        self.other_supplier = User.objects.create_user(username="supplier2", email="supplier2@example.com", password="pass")
        self.rfq = RFQ.objects.create(
            buyer=self.buyer,
            title="Cotton fabric",
            response_deadline=timezone.now() + timedelta(days=7),
            payment_terms="Net 30",
        )
        self.line_item = RFQLineItem.objects.create(
            rfq=self.rfq,
            line_number=1,
            description="Organic cotton fabric",
            quantity=100,
            unit="meter",
        )
        RFQSupplier.objects.create(rfq=self.rfq, supplier=self.supplier)
        RFQSupplier.objects.create(rfq=self.rfq, supplier=self.other_supplier)

    def test_issue_rfq_records_status_history(self):
        services.issue_rfq(self.rfq, changed_by=self.buyer)
        self.rfq.refresh_from_db()

        self.assertEqual(self.rfq.status, RFQ.Status.ISSUED)
        self.assertTrue(
            RFQStatusHistory.objects.exclude(
                rfq=self.rfq,
                previous_status=RFQ.Status.DRAFT,
                new_status=RFQ.Status.ISSUED,
            ).exists()
        )

    def test_submit_and_accept_supplier_quotation_awards_rfq(self):
        quotation = SupplierQuotation.objects.create(
            rfq=self.rfq,
            supplier=self.supplier,
            currency="USD",
            valid_until=timezone.now() + timedelta(days=30),
            payment_terms="50% upfront",
        )
        quotation.line_items.create(rfq_line_item=self.line_item, quoted_quantity=100, unit_price=12)

        services.submit_quotation(quotation, changed_by=self.supplier)
        services.accept_quotation(quotation, accepted_by=self.buyer, note="Best value")
        self.rfq.refresh_from_db()
        quotation.refresh_from_db()

        self.assertEqual(quotation.status, SupplierQuotation.Status.ACCEPTED)
        self.assertEqual(self.rfq.status, RFQ.Status.AWARDED)
        self.assertEqual(self.rfq.awarded_quotation, quotation)
        self.assertEqual(quotation.total_amount, 1200)

    def test_counteroffer_updates_quotation_when_accepted(self):
        quotation = SupplierQuotation.objects.create(rfq=self.rfq, supplier=self.supplier, currency="USD")
        quotation.line_items.create(rfq_line_item=self.line_item, quoted_quantity=100, unit_price=12)
        services.submit_quotation(quotation, changed_by=self.supplier)

        counteroffer = services.create_counteroffer(
            quotation,
            self.buyer,
            {
                "currency": "USD",
                "subtotal_amount": 1000,
                "tax_amount": 0,
                "shipping_amount": 50,
                "total_amount": 1050,
                "delivery_estimate": "14 days",
                "payment_terms": "Net 45",
                "notes": "Can you meet this target?",
            },
        )
        services.respond_to_counteroffer(counteroffer, accepted=True, responder=self.supplier)
        quotation.refresh_from_db()

        self.assertEqual(quotation.total_amount, 1050)
        self.assertEqual(quotation.delivery_estimate, "14 days")
        self.assertEqual(quotation.payment_terms, "Net 45")


class RFQWorkflowAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(username="buyer", email="buyer@example.com", password="pass")
        self.supplier = User.objects.create_user(username="supplier", email="supplier@example.com", password="pass")
        self.factory = APIRequestFactory()
        self.rfq = RFQ.objects.create(buyer=self.buyer, title="Denim jackets")
        self.line_item = RFQLineItem.objects.create(
            rfq=self.rfq,
            line_number=1,
            description="Denim jacket",
            quantity=50,
            unit="piece",
        )
        RFQSupplier.objects.create(rfq=self.rfq, supplier=self.supplier)

    def test_issue_endpoint(self):
        view = RFQViewSet.as_view({"post": "issue"})
        request = self.factory.post(f"/rfqs/{self.rfq.id}/issue/", {})
        force_authenticate(request, user=self.buyer)

        response = view(request, pk=self.rfq.id)
        self.rfq.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.rfq.status, RFQ.Status.ISSUED)

    def test_submit_endpoint(self):
        quotation = SupplierQuotation.objects.create(rfq=self.rfq, supplier=self.supplier, currency="USD")
        quotation.line_items.create(rfq_line_item=self.line_item, quoted_quantity=50, unit_price=25)
        view = SupplierQuotationViewSet.as_view({"post": "submit"})
        request = self.factory.post(f"/quotations/{quotation.id}/submit/", {})
        force_authenticate(request, user=self.supplier)

        response = view(request, pk=quotation.id)
        quotation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(quotation.status, SupplierQuotation.Status.SUBMITTED)
        self.assertEqual(quotation.total_amount, 1250)
