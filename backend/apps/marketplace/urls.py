from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryAttributeViewSet,
    CategoryViewSet,
    CertificationViewSet,
    CompareListViewSet,
    FavoriteSupplierViewSet,
    InventoryViewSet,
    PriceListViewSet,
    PricingTierViewSet,
    ProductAnswerViewSet,
    ProductAttributeValueViewSet,
    ProductBundleViewSet,
    ProductDocumentViewSet,
    ProductQuestionViewSet,
    ProductVariantViewSet,
    ProductViewSet,
    ReviewViewSet,
    SavedProductViewSet,
    SavedSearchViewSet,
    ShippingOptionViewSet,
    StockAlertViewSet,
    StorefrontViewSet,
    SupplierRatingViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("certifications", CertificationViewSet, basename="certification")
router.register("storefronts", StorefrontViewSet, basename="storefront")
router.register("supplier-ratings", SupplierRatingViewSet, basename="supplier-rating")
router.register("products", ProductViewSet, basename="product")
router.register("variants", ProductVariantViewSet, basename="product-variant")
router.register("documents", ProductDocumentViewSet, basename="product-document")
router.register("pricing-tiers", PricingTierViewSet, basename="pricing-tier")
router.register("inventory", InventoryViewSet, basename="inventory")
router.register("shipping-options", ShippingOptionViewSet, basename="shipping-option")
router.register("saved-searches", SavedSearchViewSet, basename="saved-search")
router.register("saved-products", SavedProductViewSet, basename="saved-product")
router.register("favorite-suppliers", FavoriteSupplierViewSet, basename="favorite-supplier")
router.register("reviews", ReviewViewSet, basename="review")
router.register("bundles", ProductBundleViewSet, basename="product-bundle")
router.register("price-lists", PriceListViewSet, basename="price-list")
router.register("product-questions", ProductQuestionViewSet, basename="product-question")
router.register("product-answers", ProductAnswerViewSet, basename="product-answer")
router.register("comparelists", CompareListViewSet, basename="compare-list")
router.register("stock-alerts", StockAlertViewSet, basename="stock-alert")
router.register("category-attributes", CategoryAttributeViewSet, basename="category-attribute")
router.register("product-attribute-values", ProductAttributeValueViewSet, basename="product-attribute-value")

urlpatterns = [
    path("", include(router.urls)),
]
