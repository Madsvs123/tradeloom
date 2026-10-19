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
            name="SourcingProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(blank=True, max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("closed", "Closed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=14,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("target_start_date", models.DateField(blank=True, null=True)),
                ("target_end_date", models.DateField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sourcing_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Tender",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("closed", "Closed"),
                            ("awarded", "Awarded"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("closing_at", models.DateTimeField(blank=True, null=True)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "estimated_value",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=14,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("award_notes", models.TextField(blank=True)),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tenders_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tenders",
                        to="sourcing.sourcingproject",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="TenderLot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("lot_number", models.PositiveIntegerField()),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=3,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0.001)],
                    ),
                ),
                ("unit", models.CharField(default="each", max_length=32)),
                (
                    "target_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lots",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("lot_number", "id"),
                "unique_together": {("tender", "lot_number")},
            },
        ),
        migrations.CreateModel(
            name="TenderDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "doc_type",
                    models.CharField(
                        choices=[
                            ("specification", "Specification"),
                            ("terms", "Terms and Conditions"),
                            ("drawing", "Drawing"),
                            ("boq", "Bill of Quantities"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=24,
                    ),
                ),
                ("file_name", models.CharField(max_length=255)),
                ("file_url", models.URLField()),
                ("content_type", models.CharField(blank=True, max_length=120)),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="sourcing.tender",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tender_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("tender", "id"),
            },
        ),
        migrations.CreateModel(
            name="BidPackage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("issued", "Issued"),
                            ("downloaded", "Downloaded"),
                            ("submitted", "Submitted"),
                            ("withdrawn", "Withdrawn"),
                        ],
                        default="issued",
                        max_length=16,
                    ),
                ),
                ("issued_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("downloaded_at", models.DateTimeField(blank=True, null=True)),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bid_packages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bid_packages",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("tender", "id"),
                "unique_together": {("tender", "supplier")},
            },
        ),
        migrations.CreateModel(
            name="TenderResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("withdrawn", "Withdrawn"),
                            ("under_evaluation", "Under Evaluation"),
                            ("awarded", "Awarded"),
                            ("unsuccessful", "Unsuccessful"),
                        ],
                        default="draft",
                        max_length=24,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "weighted_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=8,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "package",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="responses",
                        to="sourcing.bidpackage",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tender_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="responses",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("tender", "supplier")},
            },
        ),
        migrations.CreateModel(
            name="BidLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=3,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0.001)],
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("line_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("lead_time_days", models.PositiveIntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                (
                    "lot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bid_lines",
                        to="sourcing.tenderlot",
                    ),
                ),
                (
                    "response",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="sourcing.tenderresponse",
                    ),
                ),
            ],
            options={
                "ordering": ("response", "id"),
                "unique_together": {("response", "lot")},
            },
        ),
        migrations.CreateModel(
            name="EvaluationCriterion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("price", "Price"),
                            ("quality", "Quality"),
                            ("delivery", "Delivery"),
                            ("compliance", "Compliance"),
                            ("sustainability", "Sustainability"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=24,
                    ),
                ),
                (
                    "weight",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "max_score",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("100.00"),
                        max_digits=5,
                    ),
                ),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criteria",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("-weight", "id"),
            },
        ),
        migrations.CreateModel(
            name="BidEvaluation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "score",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("evaluated_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "criterion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations",
                        to="sourcing.evaluationcriterion",
                    ),
                ),
                (
                    "evaluator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bid_evaluations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "response",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations",
                        to="sourcing.tenderresponse",
                    ),
                ),
            ],
            options={
                "ordering": ("response", "criterion"),
                "unique_together": {("response", "criterion")},
            },
        ),
        migrations.CreateModel(
            name="ReverseAuction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=32, unique=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("open", "Open"),
                            ("paused", "Paused"),
                            ("closed", "Closed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="scheduled",
                        max_length=16,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                (
                    "reserve_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=14,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "minimum_decrement",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("1.00"),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "current_best_bid",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=14,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reverse_auctions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "current_best_bidder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="leading_auctions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auctions",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="AuctionBid",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("placed_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_winning", models.BooleanField(default=False)),
                (
                    "auction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to="sourcing.reverseauction",
                    ),
                ),
                (
                    "bidder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="auction_bids",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("amount", "-placed_at"),
            },
        ),
        migrations.CreateModel(
            name="SupplierInvitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("invited", "Invited"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                            ("withdrawn", "Withdrawn"),
                        ],
                        default="invited",
                        max_length=16,
                    ),
                ),
                ("invited_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("message", models.TextField(blank=True)),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tender_invitations_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tender_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="supplier_invitations",
                        to="sourcing.tender",
                    ),
                ),
            ],
            options={
                "ordering": ("tender", "id"),
                "unique_together": {("tender", "supplier")},
            },
        ),
        migrations.AddField(
            model_name="tender",
            name="awarded_response",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="awarded_tenders",
                to="sourcing.tenderresponse",
            ),
        ),
    ]
