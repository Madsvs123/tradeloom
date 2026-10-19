from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(SluggedModel):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="childrens_ref", null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta(SluggedModel.Meta):
        verbose_name_plural = "categories"


class Certification(SluggedModel):
    issuing_body = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)


class Storefront(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        LIVE = "live", "Live"
        SUSPENDED = "suspended", "Suspended"

    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_storefronts")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(fields=("supplier", "name"), name="marketplace_unique_supplier_storefront_name"),
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SupplierRating(TimeStampedModel):
    storefront = models.OneToOneField(Storefront, on_delete=models.CASCADE, related_name="rating")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0.00"))
    review_count = models.PositiveIntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.storefront} rating"


class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNPUBLISHED = "unpublished", "Unpublished"
        ARCHIVED = "archived", "Archived"

    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    certifications = models.ManyToManyField(Certification, related_name="products", blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    sku = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=40, default="unit")
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(fields=("storefront", "slug"), name="marketplace_unique_product_slug_per_storefront"),
            models.UniqueConstraint(
                fields=("storefront", "sku"),
                condition=~models.Q(sku=""),
                name="marketplace_unique_product_sku_per_storefront",
            ),
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def publish(self):
        if self.status == self.Status.ARCHIVED:
            raise ValidationError("Archived products cannot be published.")
        if self.minimum_order_quantity <= 1:
            raise ValidationError("A product must have a minimum order quantity of at least 1.")
        self.status = self.Status.PUBLISHED
        self.is_published = True
        self.save(update_fields=["status", "is_published", "updated_at"])

    def unpublish(self):
        if self.status not in (self.Status.PUBLISHED, self.Status.DRAFT):
            raise ValidationError(f"Cannot unpublish a product in status '{self.status}'.")
        self.status = self.Status.UNPUBLISHED
        self.is_published = False
        self.save(update_fields=["status", "is_published", "updated_at"])


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=160)
    sku = models.CharField(max_length=80)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__name", "name")
        constraints = (
            models.UniqueConstraint(fields=("product", "sku"), name="marketplace_unique_variant_sku_per_product"),
        )

    def __str__(self):
        return f"{self.product} - {self.name}"


class ProductDocument(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=160)
    document_type = models.CharField(max_length=80)
    file_url = models.URLField()
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("product__name", "title")

    def __str__(self):
        return self.title


class PricingTier(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="pricing_tiers")
    min_quantity = models.PositiveIntegerField()
    max_quantity = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ("product__name", "min_quantity")
        constraints = (
            models.UniqueConstraint(fields=("product", "min_quantity"), name="marketplace_unique_pricing_tier_min_quantity"),
        )

    def __str__(self):
        return f"{self.product} from {self.min_quantity}"


class Inventory(TimeStampedModel):
    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name="inventory")
    quantity_available = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    restock_date = models.DateField(null=True, blank=True)
    warehouse_location = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name_plural = "inventory"

    def __str__(self):
        return f"{self.variant} inventory"


class ShippingOption(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shipping_options")
    name = models.CharField(max_length=120)
    carrier = models.CharField(max_length=120, blank=True)
    origin_country = models.CharField(max_length=80)
    destination_country = models.CharField(max_length=80, blank=True)
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=7)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        ordering = ("product__name", "price")

    def __str__(self):
        return f"{self.product} via {self.name}"


class SavedSearch(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_saved_searches")
    name = models.CharField(max_length=120)
    query = models.CharField(max_length=255, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    alert_enabled = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(fields=("user", "name"), name="marketplace_unique_saved_search_name_per_user"),
        )

    def __str__(self):
        return self.name


class SavedProduct(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_saved_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="saved_by")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(fields=("user", "product"), name="marketplace_unique_saved_product_per_user"),
        )

    def __str__(self):
        return f"{self.user} saved {self.product}"


class FavoriteSupplier(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_favorite_suppliers"
    )
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="favorited_by")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(fields=("user", "storefront"), name="marketplace_unique_favorite_supplier_per_user"),
        )

    def __str__(self):
        return f"{self.user} favorited {self.storefront}"


class Review(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=(MinValueValidator(1), MaxValueValidator(5)))
    title = models.CharField(max_length=160, blank=True)
    body = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("user", "product", "storefront"),
                name="marketplace_unique_review_target_per_user",
            ),
        )

    def __str__(self):
        return f"{self.rating}/5 by {self.user}"


class ProductBundle(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="bundles")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=220, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    items = models.JSONField(default=list, blank=True)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))]
    )
    currency = models.CharField(max_length=3, default="USD")
    bundle_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(fields=("storefront", "slug"), name="marketplace_unique_bundle_slug_per_storefront"),
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def activate(self):
        if self.status == self.Status.ARCHIVED:
            raise ValidationError("Archived bundles cannot be activated.")
        if not self.items:
            raise ValidationError("A bundle must contain at least one item before it can be activated.")
        if self.discount_percent > 100:
            raise ValidationError("Bundle discount must be below 100%.")
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status", "updated_at"])
        return self

    def archive(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active bundles can be archived.")
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status", "updated_at"])
        return self


class PriceList(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="price_lists")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    entries = models.JSONField(default=list, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("storefront", "name", "status"),
                condition=models.Q(status="active"),
                name="marketplace_unique_active_price_list_per_storefront",
            ),
        )

    def __str__(self):
        return self.name

    def activate(self):
        if not self.entries:
            raise ValidationError("A price list must contain at least one entry before activation.")
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status", "updated_at"])
        return self

    def archive(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active price lists can be archived.")
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status", "updated_at"])
        return self


class ProductQuestion(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ANSWERED = "answered", "Answered"
        CLOSED = "closed", "Closed"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="questions")
    asked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="product_questions")
    body = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Question on {self.product} by {self.asked_by}"

    def close(self):
        if self.status != self.Status.OPEN:
            raise ValidationError("Only open questions can be closed.")
        self.status = self.Status.CLOSED
        self.save(update_fields=["status", "updated_at"])
        return self


class ProductAnswer(TimeStampedModel):
    question = models.ForeignKey(ProductQuestion, on_delete=models.CASCADE, related_name="answers")
    answered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="product_answers")
    body = models.TextField()
    is_official = models.BooleanField(default=False)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Answer to {self.question_id} by {self.answered_by}"


class CompareList(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_compare_lists")
    name = models.CharField(max_length=120, default="My comparison")
    items = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(fields=("user", "name"), name="marketplace_unique_compare_list_name_per_user"),
        )

    def __str__(self):
        return f"{self.user} compare list"

    def add_product(self, product_id):
        if product_id in self.items:
            raise ValidationError("This product is already in the compare list.")
        self.items = list(self.items) + [product_id]
        self.save(update_fields=["items", "updated_at"])
        return self

    def remove_product(self, product_id):
        if product_id not in self.items:
            raise ValidationError("This product is not in the compare list.")
        self.items = [item for item in self.items if item != product_id]
        self.save(update_fields=["items", "updated_at"])
        return self


class StockAlert(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRIGGERED = "triggered", "Triggered"
        DISMISSED = "dismissed", "Dismissed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stock_alerts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_alerts")
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name="stock_alerts")
    threshold_quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("user", "product", "variant"),
                condition=models.Q(status="active"),
                name="marketplace_unique_active_stock_alert_per_user_product",
            ),
        )

    def __str__(self):
        return f"Alert {self.user} for {self.product}"

    def trigger(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active alerts can be triggered.")
        self.status = self.Status.TRIGGERED
        self.triggered_at = timezone.now()
        self.save(update_fields=["status", "triggered_at", "updated_at"])
        return self

    def dismiss(self):
        if self.status != self.Status.DISMISSED:
            raise ValidationError("This alert is already dismissed.")
        self.status = self.Status.DISMISSED
        self.save(update_fields=["status", "updated_at"])
        return self


class CategoryAttribute(TimeStampedModel):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"
        SELECT = "select", "Select"

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="attributes")
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=120)
    field_type = models.CharField(max_length=16, choices=FieldType.choices, default=FieldType.TEXT)
    options = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)

    class Meta:
        ordering = ("category__name", "name")
        constraints = (
            models.UniqueConstraint(fields=("category", "code"), name="marketplace_unique_attribute_code_per_category"),
        )

    def __str__(self):
        return f"{self.category}: {self.name}"


class ProductAttributeValue(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name="values")
    value = models.JSONField(default=None, blank=True, null=True)

    class Meta:
        ordering = ("product__name", "attribute__name")
        constraints = (
            models.UniqueConstraint(
                fields=("product", "attribute"), name="marketplace_unique_attribute_value_per_product"
            ),
        )

    def __str__(self):
        return f"{self.product}: {self.attribute.code} = {self.value}"
