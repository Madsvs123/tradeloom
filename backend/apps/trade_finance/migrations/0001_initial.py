import decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LetterOfCredit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "lc_type",
                    models.CharField(
                        choices=[
                            ("sight", "Sight"),
                            ("usance", "Usance"),
                            ("standby", "Standby"),
                            ("revolving", "Revolving"),
                        ],
                        default="sight",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("amended", "Amended"),
                            ("confirmed", "Confirmed"),
                            ("negotiated", "Negotiated"),
                            ("matured", "Matured"),
                            ("closed", "Closed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("issuing_bank", models.CharField(blank=True, max_length=255)),
                ("advising_bank", models.CharField(blank=True, max_length=255)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("expiry_date", models.DateField()),
                ("latest_shipment_date", models.DateField(blank=True, null=True)),
                ("terms", models.TextField(blank=True)),
                ("document_requirements", models.TextField(blank=True)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lcs_applicant",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "beneficiary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lcs_beneficiary",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="InvoiceFinancingRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("invoice_reference", models.CharField(max_length=64)),
                (
                    "invoice_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "requested_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "requested_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("5.00"),
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("tenor_days", models.PositiveIntegerField(default=30)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("under_review", "Under Review"),
                            ("offered", "Offered"),
                            ("accepted", "Accepted"),
                            ("funded", "Funded"),
                            ("repaid", "Repaid"),
                            ("rejected", "Rejected"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("funded_at", models.DateTimeField(blank=True, null=True)),
                ("repaid_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="financing_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="FactoringAgreement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "agreement_type",
                    models.CharField(
                        choices=[
                            ("recourse", "Recourse"),
                            ("non_recourse", "Non-Recourse"),
                        ],
                        default="recourse",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("terminated", "Terminated"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "credit_limit",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "advance_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("80.00"),
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "discount_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("3.00"),
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("signed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "factor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="factoring_factor_for",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="factoring_agreements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CreditInsurancePolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("insurer", models.CharField(blank=True, max_length=255)),
                ("policy_number", models.CharField(blank=True, max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "coverage_limit",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "premium",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "insured",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="credit_insurance_policies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="BankGuarantee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "guarantee_type",
                    models.CharField(
                        choices=[
                            ("bid", "Bid Bond"),
                            ("performance", "Performance"),
                            ("advance_payment", "Advance Payment"),
                            ("warranty", "Warranty"),
                        ],
                        default="performance",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("claimed", "Claimed"),
                            ("released", "Released"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("bank", models.CharField(blank=True, max_length=255)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("issue_date", models.DateField(blank=True, null=True)),
                ("expiry_date", models.DateField(blank=True, null=True)),
                ("claim_notes", models.TextField(blank=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="guarantees_applicant",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "beneficiary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="guarantees_beneficiary",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="FinancingOffer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                            ("expired", "Expired"),
                        ],
                        default="draft",
                        max_length=12,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "rate",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("tenor_days", models.PositiveIntegerField(default=30)),
                (
                    "fees",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "offered_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="financing_offers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offers",
                        to="trade_finance.invoicefinancingrequest",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="FinanceDisbursement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("approved", "Approved"),
                            ("disbursed", "Disbursed"),
                            ("failed", "Failed"),
                        ],
                        default="requested",
                        max_length=12,
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("bank_transfer", "Bank Transfer"),
                            ("wire", "Wire"),
                            ("check", "Check"),
                            ("other", "Other"),
                        ],
                        default="bank_transfer",
                        max_length=16,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("disbursed_at", models.DateTimeField(blank=True, null=True)),
                ("failure_reason", models.TextField(blank=True)),
                (
                    "agreement",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disbursements",
                        to="trade_finance.factoringagreement",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="finance_disbursements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disbursements",
                        to="trade_finance.invoicefinancingrequest",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="LcAmendment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("applied", "Applied"),
                        ],
                        default="requested",
                        max_length=16,
                    ),
                ),
                ("amendment_type", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True)),
                (
                    "new_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=16,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("new_expiry_date", models.DateField(blank=True, null=True)),
                ("requested_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("applied_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lc_amendments_approved",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "lc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="amendments",
                        to="trade_finance.letterofcredit",
                    ),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lc_amendments_requested",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-requested_at",),
            },
        ),
        migrations.CreateModel(
            name="RepaymentSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("due_date", models.DateField()),
                (
                    "principal",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "interest",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "total_due",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("due", "Due"),
                            ("paid", "Paid"),
                            ("late", "Late"),
                            ("defaulted", "Defaulted"),
                        ],
                        default="scheduled",
                        max_length=12,
                    ),
                ),
                (
                    "paid_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=16,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                (
                    "paid_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="repayments_recorded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="repayment_schedules",
                        to="trade_finance.invoicefinancingrequest",
                    ),
                ),
            ],
            options={
                "ordering": ("due_date", "id"),
            },
        ),
    ]
