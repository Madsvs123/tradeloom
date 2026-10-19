import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


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
            name="VendorAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                ("legal_name", models.CharField(max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("active", "Active"), ("suspended", "Suspended")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("country", models.CharField(blank=True, max_length=2)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vendor_accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorTeamMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "role",
                    models.CharField(
                        choices=[("owner", "Owner"), ("manager", "Manager"), ("operator", "Operator")],
                        default="operator",
                        max_length=16,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vendor_memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "unique_together": {("vendor", "user")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorPerformanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("on_time_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("quality_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("fulfillment_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("overall_score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("metrics", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")], default="draft", max_length=16
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "published_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="published_performance_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="performance_records",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("vendor", "period")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorScorecard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(max_length=32)),
                ("criteria", models.JSONField(blank=True, default=list)),
                ("score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("band", models.CharField(default="bronze", max_length=16)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decided_vendor_scorecards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vendor_scorecards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scorecards",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("document_type", models.CharField(max_length=80)),
                ("file_url", models.URLField()),
                (
                    "status",
                    models.CharField(
                        choices=[("uploaded", "Uploaded"), ("verified", "Verified"), ("rejected", "Rejected")],
                        default="uploaded",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vendor_documents",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_vendor_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PriceBookItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sku", models.CharField(max_length=80)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("min_quantity", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_book_items",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("vendor", "sku"),
                "unique_together": {("vendor", "sku", "currency")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PriceChangeRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("requested_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("reason", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("decision_note", models.TextField(blank=True)),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="decided_price_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "price_book_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_change_requests",
                        to="vendor_ops.pricebookitem",
                    ),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="price_change_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorAnnouncement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("body", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("starts_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vendor_announcements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="announcements",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ServiceRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_number", models.CharField(blank=True, max_length=40)),
                ("customer_name", models.CharField(blank=True, max_length=180)),
                ("rating", models.PositiveSmallIntegerField(default=5)),
                ("review", models.TextField(blank=True)),
                ("is_public", models.BooleanField(default=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_ratings",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InventoryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sku", models.CharField(max_length=80)),
                ("name", models.CharField(max_length=180)),
                ("quantity_on_hand", models.IntegerField(default=0)),
                ("quantity_reserved", models.IntegerField(default=0)),
                ("reorder_point", models.IntegerField(default=0)),
                ("unit_cost", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory_items",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("vendor", "sku"),
                "unique_together": {("vendor", "sku")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InventoryAdjustment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("delta", models.IntegerField()),
                ("reason", models.CharField(blank=True, max_length=160)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inventory_adjustments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="adjustments",
                        to="vendor_ops.inventoryitem",
                    ),
                ),
            ],
            options={},
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PriceBookChange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("previous_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("new_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("note", models.CharField(blank=True, max_length=160)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="changes",
                        to="vendor_ops.pricebookitem",
                    ),
                ),
            ],
            options={},
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="IncomingOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_number", models.CharField(max_length=40)),
                ("buyer_name", models.CharField(blank=True, max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("acknowledged", "Acknowledged"),
                            ("allocated", "Allocated"),
                            ("shipped", "Shipped"),
                            ("closed", "Closed"),
                        ],
                        default="new",
                        max_length=16,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incoming_orders",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("vendor", "order_number")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorRFQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("rfq_reference", models.CharField(max_length=40)),
                ("title", models.CharField(max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("invited", "Invited"),
                            ("drafting", "Drafting"),
                            ("submitted", "Submitted"),
                            ("lost", "Lost"),
                            ("won", "Won"),
                        ],
                        default="invited",
                        max_length=16,
                    ),
                ),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("quoted_total", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="rfqs", to="vendor_ops.vendoraccount"
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("vendor", "rfq_reference")},
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CustomerRelationshipNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_name", models.CharField(max_length=180)),
                ("body", models.TextField()),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_notes",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={},
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorPayout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("reference", models.CharField(blank=True, max_length=80)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payouts",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorDispute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_number", models.CharField(blank=True, max_length=40)),
                ("subject", models.CharField(max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("in_review", "In review"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disputes",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={},
            bases=("vendor_ops", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="VendorReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("period", models.CharField(blank=True, max_length=32)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="vendor_ops.vendoraccount",
                    ),
                ),
            ],
            options={},
            bases=("vendor_ops", "TimeStampedModel"),
        ),
    ]
