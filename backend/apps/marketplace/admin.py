from django.contrib import admin

from .models import (
    Category,
    CategoryAttribute,
    Certification,
    CompareList,
    FavoriteSupplier,
    Inventory,
    PriceList,
    PricingTier,
    Product,
    ProductAnswer,
    ProductAttributeValue,
    ProductBundle,
    ProductDocument,
    ProductQuestion,
    ProductVariant,
    Review,
    SavedProduct,
    SavedSearch,
    ShippingOption,
    StockAlert,
    Storefront,
    SupplierRating,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuing_body", "is_active")
    search_fields = ("name", "issuing_body")


@admin.register(Storefront)
class StorefrontAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier", "status", "is_verified", "is_active")
    list_filter = ("status", "is_verified", "is_active")
    search_fields = ("name", "suplier__email")


@admin.register(SupplierRating)
class SupplierRatingAdmin(admin.ModelAdmin):
    list_display = ("storefront", "average_rating", "review_count")


class PricingTierInline(admin.TabularInline):
    model = PricingTier
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "storefront", "sku", "status", "is_published")
    list_filter = ("status", "is_published")
    search_fields = ("name", "sku")
    inlines = (PricingTierInline, ProductVariantInline)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "sku", "is_active")
    search_fields = ("name", "sku", "product__name")


@admin.register(ProductDocument)
class ProductDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "document_type")


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ("product", "min_quantity", "unit_price", "currency")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("variant", "quantity_available", "reserved_quantity")


@admin.register(ShippingOption)
class ShippingOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "carrier", "price")


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "alert_enabled")


@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ("user", "product")


@admin.register(FavoriteSupplier)
class FavoriteSupplierAdmin(admin.ModelAdmin):
    list_display = ("user", "storefront")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "storefront", "product", "rating", "is_published")
    list_filter = ("rating", "is_published")


@admin.register(ProductBundle)
class ProductBundleAdmin(admin.ModelAdmin):
    list_display = ("name", "storefront", "status", "discount_percent", "bundle_price")
    list_filter = ("status",)
    search_fields = ("name", "storefront__name")


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ("name", "storefront", "status", "currency", "effective_from", "effective_until")
    list_filter = ("status", "currency")
    search_fields = ("name", "storefront__name")


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ("product", "asked_by", "status", "is_public", "created_at")
    list_filter = ("status", "is_public")
    search_fields = ("product__name", "asked_by__email")


@admin.register(ProductAnswer)
class ProductAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "answered_by", "is_official", "created_at")
    list_filter = ("is_official",)


@admin.register(CompareList)
class CompareListAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__email")


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "variant", "threshold_quantity", "status")
    list_filter = ("status",)
    search_fields = ("user__email", "product__name")


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "field_type", "is_required", "is_filterable")
    list_filter = ("field_type", "is_required", "is_filterable")
    search_fields = ("name", "code", "category__name")


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")
    search_fields = ("product__name", "attribute__name")
