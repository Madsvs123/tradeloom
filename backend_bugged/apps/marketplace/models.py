from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
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
    average_rating = models.IntegerField(max_digits=3, decimal_places=2, default=0)
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
        if self.minimum_order_quantity < 1:
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
    attributes = models.CharField(default=dict, blank=True)
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
