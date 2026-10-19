from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategoryAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("code", models.SlugField(max_length=120)),
                ("field_type", models.CharField(choices=[("text", "Text"), ("number", "Number"), ("boolean", "Boolean"), ("select", "Select")], default="text", max_length=16)),
                ("options", models.JSONField(blank=True, default=list)),
                ("is_required", models.BooleanField(default=False)),
                ("is_filterable", models.BooleanField(default=False)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attributes", to="marketplace.category")),
            ],
            options={"ordering": ("category__name", "name")},
        ),
        migrations.CreateModel(
            name="CompareList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(default="My comparison", max_length=120)),
                ("items", models.JSONField(blank=True, default=list)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marketplace_compare_lists", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="PriceList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")], default="draft", max_length=16)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("entries", models.JSONField(blank=True, default=list)),
                ("effective_from", models.DateField(blank=True, null=True)),
                ("effective_until", models.DateField(blank=True, null=True)),
                ("storefront", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="price_lists", to="marketplace.storefront")),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ProductAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("body", models.TextField()),
                ("is_official", models.BooleanField(default=False)),
                ("answered_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="product_answers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("created_at",)},
        ),
        migrations.CreateModel(
            name="ProductBundle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("slug", models.SlugField(blank=True, max_length=220)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")], default="draft", max_length=16)),
                ("items", models.JSONField(blank=True, default=list)),
                ("discount_percent", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("bundle_price", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("storefront", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bundles", to="marketplace.storefront")),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ProductQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("body", models.TextField()),
                ("status", models.CharField(choices=[("open", "Open"), ("answered", "Answered"), ("closed", "Closed")], default="open", max_length=16)),
                ("is_public", models.BooleanField(default=True)),
                ("asked_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="product_questions", to=settings.AUTH_USER_MODEL)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="marketplace.product")),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.JSONField(blank=True, default=None, null=True)),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="values", to="marketplace.categoryattribute")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attribute_values", to="marketplace.product")),
            ],
            options={"ordering": ("product__name", "attribute__name")},
        ),
        migrations.CreateModel(
            name="StockAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("threshold_quantity", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("active", "Active"), ("triggered", "Triggered"), ("dismissed", "Dismissed")], default="active", max_length=16)),
                ("triggered_at", models.DateTimeField(blank=True, null=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_alerts", to="marketplace.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_alerts", to=settings.AUTH_USER_MODEL)),
                ("variant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="stock_alerts", to="marketplace.productvariant")),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddField(
            model_name="productanswer",
            name="question",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="marketplace.productquestion"),
        ),
        migrations.AddConstraint(
            model_name="categoryattribute",
            constraint=models.UniqueConstraint(fields=("category", "code"), name="marketplace_unique_attribute_code_per_category"),
        ),
        migrations.AddConstraint(
            model_name="comparelist",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="marketplace_unique_compare_list_name_per_user"),
        ),
        migrations.AddConstraint(
            model_name="pricelist",
            constraint=models.UniqueConstraint(condition=models.Q(("status", "active")), fields=("storefront", "name", "status"), name="marketplace_unique_active_price_list_per_storefront"),
        ),
        migrations.AddConstraint(
            model_name="productattributevalue",
            constraint=models.UniqueConstraint(fields=("product", "attribute"), name="marketplace_unique_attribute_value_per_product"),
        ),
        migrations.AddConstraint(
            model_name="productbundle",
            constraint=models.UniqueConstraint(fields=("storefront", "slug"), name="marketplace_unique_bundle_slug_per_storefront"),
        ),
        migrations.AddConstraint(
            model_name="stockalert",
            constraint=models.UniqueConstraint(condition=models.Q(("status", "active")), fields=("user", "product", "variant"), name="marketplace_unique_active_stock_alert_per_user_product"),
        ),
    ]
