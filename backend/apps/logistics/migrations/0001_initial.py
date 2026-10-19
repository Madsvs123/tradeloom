import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import apps.logistics.models


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
            name="Warehouse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("country", models.CharField(max_length=2)),
                ("city", models.CharField(max_length=80)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("code",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WarehouseZone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32)),
                ("name", models.CharField(max_length=120)),
                (
                    "zone_type",
                    models.CharField(
                        choices=[
                            ("storage", "Storage"),
                            ("picking", "Picking"),
                            ("receiving", "Receiving"),
                            ("shipping", "Shipping"),
                            ("quarantine", "Quarantine"),
                        ],
                        default="storage",
                        max_length=16,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="zones",
                        to="logistics.warehouse",
                    ),
                ),
            ],
            options={
                "ordering": ("warehouse", "code"),
                "unique_together": {("warehouse", "code")},
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="WarehouseBin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=32)),
                ("capacity", models.PositiveIntegerField(default=0)),
                ("description", models.CharField(blank=True, max_length=160)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="bins", to="logistics.warehousezone"
                    ),
                ),
            ],
            options={
                "ordering": ("zone", "code"),
                "unique_together": {("zone", "code")},
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Dock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("dock_type", models.CharField(default="shipping", max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="docks", to="logistics.warehouse"
                    ),
                ),
            ],
            options={
                "unique_together": {("warehouse", "name")},
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CarrierAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("scac", models.CharField(blank=True, max_length=16)),
                ("account_number", models.CharField(blank=True, max_length=80)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RateTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("origin", models.CharField(max_length=80)),
                ("destination", models.CharField(max_length=80)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("base_rate", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("min_charge", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("effective_from", models.DateField(blank=True, null=True)),
                ("effective_until", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "carrier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rate_tables",
                        to="logistics.carrieraccount",
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Incoterm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=8, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="FreightQuote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("origin", models.CharField(max_length=80)),
                ("destination", models.CharField(max_length=80)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("transit_days", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("offered", "Offered"), ("accepted", "Accepted"), ("expired", "Expired")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                (
                    "carrier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="quotes", to="logistics.carrieraccount"
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ShipmentPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("planned", "Planned"),
                            ("in_transit", "In transit"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("origin", models.CharField(blank=True, max_length=120)),
                ("destination", models.CharField(blank=True, max_length=120)),
                ("planned_ship_date", models.DateField(blank=True, null=True)),
                (
                    "carrier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="logistics.carrieraccount",
                    ),
                ),
                (
                    "freight_quote",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="logistics.freightquote",
                    ),
                ),
                (
                    "incoterm",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="logistics.incoterm"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="shipment_plans",
                        to="logistics.warehouse",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="AdvancedShippingNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.CharField(max_length=40, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("sent", "Sent"), ("acknowledged", "Acknowledged")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="asns",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="PackingList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.CharField(max_length=40, unique=True)),
                ("package_count", models.PositiveIntegerField(default=0)),
                ("gross_weight_kg", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("notes", models.TextField(blank=True)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="packing_lists",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Pallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sscc", models.CharField(blank=True, max_length=40)),
                ("weight_kg", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                (
                    "packing_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="pallets", to="logistics.packinglist"
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="Carton",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sku", models.CharField(blank=True, max_length=80)),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "packing_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cartons",
                        to="logistics.packinglist",
                    ),
                ),
                (
                    "pallet",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cartons",
                        to="logistics.pallet",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="TrackingEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(max_length=80)),
                ("location", models.CharField(blank=True, max_length=160)),
                ("description", models.TextField(blank=True)),
                ("occurred_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tracking_events",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={
                "ordering": ("occurred_at",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="DeliveryAppointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("scheduled_at", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("confirmed", "Confirmed"),
                            ("completed", "Completed"),
                            ("missed", "Missed"),
                        ],
                        default="requested",
                        max_length=16,
                    ),
                ),
                (
                    "dock",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="logistics.dock"
                    ),
                ),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ReceivingInspection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("passed", "Passed"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "inspector",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inspections",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="InventoryCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "number",
                    models.CharField(
                        default=apps.logistics.models._inventory_count_reference, max_length=40, unique=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("counted", "Counted"), ("reconciled", "Reconciled")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("counted_at", models.DateTimeField(blank=True, null=True)),
                ("reconciled_at", models.DateTimeField(blank=True, null=True)),
                ("items", models.JSONField(blank=True, default=list)),
                ("notes", models.TextField(blank=True)),
                (
                    "counted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inventory_counts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory_counts",
                        to="logistics.warehouse",
                    ),
                ),
                (
                    "zone",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inventory_counts",
                        to="logistics.warehousezone",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="ShipmentDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("document_type", models.CharField(max_length=80)),
                ("title", models.CharField(max_length=180)),
                ("file_url", models.URLField()),
                ("reference", models.CharField(blank=True, max_length=80)),
                (
                    "status",
                    models.CharField(
                        choices=[("uploaded", "Uploaded"), ("verified", "Verified"), ("rejected", "Rejected")],
                        default="uploaded",
                        max_length=16,
                    ),
                ),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipment_documents",
                        to="logistics.shipmentplan",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_shipment_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="HazardousDeclaration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("hazard_class", models.CharField(max_length=40)),
                ("un_number", models.CharField(max_length=16)),
                ("proper_shipping_name", models.CharField(max_length=180)),
                ("packing_group", models.CharField(blank=True, max_length=16)),
                ("net_quantity_kg", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("emergency_contact", models.CharField(blank=True, max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
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
                        related_name="decided_hazardous_declarations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hazardous_declarations",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="DamageClaim",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("description", models.TextField()),
                ("claimed_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("under_review", "Under review"),
                            ("approved", "Approved"),
                            ("denied", "Denied"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="claims", to="logistics.shipmentplan"
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="RouteMilestone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("sequence", models.PositiveIntegerField(default=1)),
                ("expected_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="milestones",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={
                "ordering": ("shipment_plan", "sequence"),
            },
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="CustomsDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("document_type", models.CharField(max_length=80)),
                ("reference", models.CharField(blank=True, max_length=80)),
                ("file_url", models.URLField(blank=True)),
                ("cleared", models.BooleanField(default=False)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customs_documents",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
        migrations.CreateModel(
            name="LogisticsException",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=40)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("investigating", "Investigating"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution", models.TextField(blank=True)),
                (
                    "shipment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exceptions",
                        to="logistics.shipmentplan",
                    ),
                ),
            ],
            options={},
            bases=("logistics", "TimeStampedModel"),
        ),
    ]
