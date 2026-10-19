import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=180)),
                ("is_active", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="childrens_ref", to="marketplace.category")),
            ],
            options={"verbose_name_plural": "categories", "ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Certification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=180)),
                ("is_active", models.BooleanField(default=True)),
                ("issuing_body", models.CharField(blank=True, max_length=160)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Storefront",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(blank=True, max_length=200, unique=True)),
                ("description", models.TextField(blank=True)),
                ("logo_url", models.URLField(blank=True)),
                ("website", models.URLField(blank=True)),
                ("country", models.CharField(blank=True, max_length=80)),
                ("city", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("live", "Live"), ("suspended", "Suspended")], default="draft", max_length=16)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_storefronts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220)),
                ("sku", models.CharField(blank=True, max_length=80)),
                ("description", models.TextField(blank=True)),
                ("unit", models.CharField(default="unit", max_length=40)),
                ("minimum_order_quantity", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("unpublished", "Unpublished"), ("archived", "Archived")], default="draft", max_length=16)),
                ("is_published", models.BooleanField(default=False)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="marketplace.category")),
                ("certifications", models.ManyToManyField(blank=True, related_name="products", to="marketplace.certification")),
                ("storefront", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="products", to="marketplace.storefront")),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="FavoriteSupplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True)),
                ("storefront", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorited_by", to="marketplace.storefront")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_favorite_suppliers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="PricingTier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("min_quantity", models.PositiveIntegerField()),
                ("max_quantity", models.PositiveIntegerField(blank=True, null=True)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pricing_tiers", to="marketplace.product")),
            ],
            options={"ordering": ("product__name", "min_quantity")},
        ),
        migrations.CreateModel(
            name="ProductDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=160)),
                ("document_type", models.CharField(max_length=80)),
                ("file_url", models.URLField()),
                ("expires_at", models.DateField(blank=True, null=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="marketplace.product")),
            ],
            options={"ordering": ("product__name", "title")},
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("sku", models.CharField(max_length=80)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="marketplace.product")),
            ],
            options={"ordering": ("product__name", "name")},
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("title", models.CharField(blank=True, max_length=160)),
                ("body", models.TextField(blank=True)),
                ("is_verified_purchase", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(default=True)),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="marketplace.product")),
                ("storefront", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="marketplace.storefront")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_reviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="SavedProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_by", to="marketplace.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_saved_products", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="SavedSearch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("query", models.CharField(blank=True, max_length=255)),
                ("filters", models.JSONField(blank=True, default=dict)),
                ("alert_enabled", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_saved_searches", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ShippingOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("carrier", models.CharField(blank=True, max_length=120)),
                ("origin_country", models.CharField(max_length=80)),
                ("destination_country", models.CharField(blank=True, max_length=80)),
                ("estimated_days_min", models.PositiveIntegerField(default=1)),
                ("estimated_days_max", models.PositiveIntegerField(default=7)),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shipping_options", to="marketplace.product")),
            ],
            options={"ordering": ("product__name", "price")},
        ),
        migrations.CreateModel(
            name="SupplierRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("average_rating", models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ("review_count", models.PositiveIntegerField(default=0)),
                ("on_time_delivery_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("response_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("storefront", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="rating", to="marketplace.storefront")),
            ],
        ),
        migrations.CreateModel(
            name="Inventory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("quantity_available", models.PositiveIntegerField(default=0)),
                ("reserved_quantity", models.PositiveIntegerField(default=0)),
                ("restock_date", models.DateField(blank=True, null=True)),
                ("warehouse_location", models.CharField(blank=True, max_length=160)),
                ("variant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="inventory", to="marketplace.productvariant")),
            ],
            options={"verbose_name_plural": "inventory"},
        ),
        migrations.AddConstraint(
            model_name="storefront",
            constraint=models.UniqueConstraint(fields=("supplier", "name"), name="marketplace_unique_supplier_storefront_name"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(fields=("storefront", "slug"), name="marketplace_unique_product_slug_per_storefront"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(condition=models.Q(("sku", ""), _negated=True), fields=("storefront", "sku"), name="marketplace_unique_product_sku_per_storefront"),
        ),
        migrations.AddConstraint(
            model_name="favoritesupplier",
            constraint=models.UniqueConstraint(fields=("user", "storefront"), name="marketplace_unique_favorite_supplier_per_user"),
        ),
        migrations.AddConstraint(
            model_name="pricingtier",
            constraint=models.UniqueConstraint(fields=("product", "min_quantity"), name="marketplace_unique_pricing_tier_min_quantity"),
        ),
        migrations.AddConstraint(
            model_name="productvariant",
            constraint=models.UniqueConstraint(fields=("product", "sku"), name="marketplace_unique_variant_sku_per_product"),
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(fields=("user", "product", "storefront"), name="marketplace_unique_review_target_per_user"),
        ),
        migrations.AddConstraint(
            model_name="savedproduct",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="marketplace_unique_saved_product_per_user"),
        ),
        migrations.AddConstraint(
            model_name="savedsearch",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="marketplace_unique_saved_search_name_per_user"),
        ),
    ]

