from rest_framework import serializers

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


class CategorySerializer(serializers.ModelSerializer):
    child_count = serializers.IntegerField(source="childrens_ref.count", read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "description", "is_active", "children_count", "created_at", "updated_at")
        read_only_fields = ("id", "slug", "child_count", "created_at", "updated_at")


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
    pricing_tiers = PricingTierSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    attribute_values = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "slug", "status", "is_published", "created_at", "updated_at")

    def get_attribute_values(self, obj):
        return {value.attribute.code: value.value for value in obj.attribute_values.select_related("attribute")}


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


class ProductBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBundle
        fields = "__all__"
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ProductQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = ProductQuestion
        fields = "__all__"
        read_only_fields = ("id", "asked_by", "status", "created_at", "updated_at")

    def get_answers(self, obj):
        return ProductAnswerSerializer(obj.answers.select_related("answered_by"), many=True).data


class ProductAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAnswer
        fields = "__all__"
        read_only_fields = ("id", "answered_by", "created_at", "updated_at")


class CompareListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompareList
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class StockAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAlert
        fields = "__all__"
        read_only_fields = ("id", "user", "status", "triggered_at", "created_at", "updated_at")


class CategoryAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAttribute
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
