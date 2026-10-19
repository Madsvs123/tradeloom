import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.finance.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TimeStampedModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Wallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[("buyer", "Buyer"), ("supplier", "Supplier"), ("platform", "Platform")],
                        default="buyer",
                        max_length=16,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("available", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("held", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="wallets", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "ordering": ("owner", "currency"),
                "unique_together": {("owner", "kind", "currency")},
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="LedgerAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=160)),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("asset", "Asset"),
                            ("liability", "Liability"),
                            ("revenue", "Revenue"),
                            ("expense", "Expense"),
                        ],
                        max_length=16,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("code",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="TransactionTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80, unique=True)),
                ("color", models.CharField(default="default", max_length=16)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="LedgerEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("memo", models.CharField(blank=True, max_length=255)),
                ("reference", models.CharField(blank=True, max_length=80)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("posted", "Posted"), ("void", "Void")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("posted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "credit_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="credits",
                        to="finance.ledgeraccount",
                    ),
                ),
                (
                    "debit_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="debits",
                        to="finance.ledgeraccount",
                    ),
                ),
                (
                    "posted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(blank=True, related_name="ledger_entries", to="finance.transactiontag"),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="EscrowAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.PositiveIntegerField(blank=True, null=True)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("funded", "Funded"),
                            ("released", "Released"),
                            ("refunded", "Refunded"),
                            ("closed", "Closed"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                (
                    "buyer_wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="buyer_escrows", to="finance.wallet"
                    ),
                ),
                (
                    "seller_wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="seller_escrows", to="finance.wallet"
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="EscrowHold",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[("held", "Held"), ("released", "Released"), ("refunded", "Refunded")],
                        default="held",
                        max_length=16,
                    ),
                ),
                (
                    "escrow",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="holds",
                        to="finance.escrowaccount",
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="SettlementBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(max_length=40, unique=True)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("gross_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("fee_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("net_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("settled", "Settled")], default="open", max_length=16
                    ),
                ),
                ("settled_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PaymentRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reference",
                    models.CharField(
                        default=apps.finance.models._payment_run_reference, max_length=40, unique=True
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=255)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("scheduled", "Scheduled"),
                            ("executing", "Executing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("executed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "executed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PayoutInstruction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("destination", models.CharField(blank=True, max_length=160)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("approved", "Approved"),
                            ("sent", "Sent"),
                            ("failed", "Failed"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "payment_run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payouts",
                        to="finance.paymentrun",
                    ),
                ),
                (
                    "settlement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payouts",
                        to="finance.settlementbatch",
                    ),
                ),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="payouts", to="finance.wallet"
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account_name", models.CharField(max_length=180)),
                ("bank_name", models.CharField(max_length=180)),
                (
                    "kind",
                    models.CharField(
                        choices=[("checking", "Checking"), ("savings", "Savings"), ("escrow", "Escrow")],
                        default="checking",
                        max_length=16,
                    ),
                ),
                ("account_number", models.CharField(max_length=80)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("swift_code", models.CharField(blank=True, max_length=16)),
                ("iban", models.CharField(blank=True, max_length=48)),
                ("is_active", models.BooleanField(default=True)),
                ("verified", models.BooleanField(default=False)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="bank_accounts", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_bank_accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ExpenseCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("code",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InvoiceMatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reference",
                    models.CharField(
                        default=apps.finance.models._invoice_match_reference, max_length=40, unique=True
                    ),
                ),
                ("invoice_number", models.CharField(max_length=80)),
                ("order_reference", models.CharField(blank=True, max_length=80)),
                ("counterparty_name", models.CharField(blank=True, max_length=180)),
                ("expected_amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("actual_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("variance", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("matched", "Matched"),
                            ("partial", "Partial"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("rejection_reason", models.TextField(blank=True)),
                ("matched_at", models.DateTimeField(blank=True, null=True)),
                (
                    "matched_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("invoice_number", "currency")},
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="FinanceApproval",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("target_type", models.CharField(max_length=80)),
                ("target_id", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("note", models.TextField(blank=True)),
                ("decision_note", models.TextField(blank=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decided_finance_approvals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requested_finance_approvals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="TaxRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("jurisdiction", models.CharField(max_length=80)),
                ("tax_id", models.CharField(max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tax_registrations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("owner", "jurisdiction")},
            },
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="TaxAssessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("taxable_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("filed", "Filed")], default="draft", max_length=16
                    ),
                ),
                ("filed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "registration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assessments",
                        to="finance.taxregistration",
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CreditFacility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("limit", models.DecimalField(decimal_places=2, max_digits=14)),
                ("drawn", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("closed", "Closed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("interest_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                (
                    "borrower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="credit_facilities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CreditDraw",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="requested",
                        max_length=16,
                    ),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="draws", to="finance.creditfacility"
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReconciliationBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(max_length=40, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("matched", "Matched")], default="open", max_length=16
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("expected_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("actual_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("run_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReconciliationItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(max_length=80)),
                ("expected_amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("actual_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("matched", models.BooleanField(default=False)),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="finance.reconciliationbatch",
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="FinanceStatement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("opening_balance", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("closing_balance", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")], default="draft", max_length=16
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="finance_statements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=("finance", "TimeStampedModel"),
        ),
    ]
