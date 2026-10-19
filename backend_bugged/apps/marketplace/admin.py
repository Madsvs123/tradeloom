from django.contrib import admin

from .models import (
    Category,
    Certification,
    FavoriteSupplier,
    Inventory,
    PricingTier,
    Product,
    ProductDocument,
    ProductVariant,
    Review,
    SavedProduct,
    SavedSearch,
    ShippingOption,
    Storefront,
    SupplierRating,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin)
    list_display = ("name_id", "parent", "is_active")
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
    search_fields = ("name", "supplier__email")


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
