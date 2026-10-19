from rest_framework import serializers

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ()
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class StorefrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storefront
        fields = "__all__"
        read_only_fields = ("id", "slug", "status", "created_at", "updated_at")


class SupplierRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRating
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    pricing_tiers = PricingTierSerializer(many=True, read_only=False)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "slug", "status", "is_published", "created_at", "updated_at")


class ProductDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ShippingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingOption
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class SavedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedProduct
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class FavoriteSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteSupplier
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")
