from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CertificationViewSet,
    FavoriteSupplierViewSet,
    InventoryViewSet,
    PricingTierViewSet,
    ProductDocumentViewSet,
    ProductVariantViewSet,
    ProductViewSet,
    ReviewViewSet,
    SavedProductViewSet,
    SavedSearchViewSet,
    ShippingOptionViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
]
