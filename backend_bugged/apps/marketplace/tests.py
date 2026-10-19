from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import (
    Category,
    FavoriteSupplier,
    Product,
    ProductVariant,
    SavedProduct,
    SavedSearch,
    Storefront,
)
from .urls import router
from .views import ProductViewSet, SavedProductViewSet, SavedSearchViewSet, StorefrontViewSet


User = get_user_model()


class MarketplaceFactoryMixin
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email="buyer@example.com", password="pass")
        self.supplier = User.objects.create_user(
            email="supplier@example.com",
            password="pass",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="pass",
        )
        self.category = Category.objects.create(name="Cotton")
        self.storefront = Storefront.objects.create(
            supplier=self.supplier,
            name="Nile Textiles",
            country="Egypt",
        )
        self.product = Product.objects.create(
            storefront=self.storefront,
            category=self.category,
            name="Organic Cotton Roll",
            sku="COT-001",
            is_published=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Natural / 50m",
            sku="COT-001-NAT-50",
        )


class MarketplaceModelTests(MarketplaceFactoryMixin, TestCase):
    def test_slugs_are_generated_for_core_catalog_models(self):
        self.assertEqual(self.category.slug, "cotton")
        self.assertEqual(self.storefront.slug, "nile-textiles")
        self.assertEqual(self.product.slug, "organic-cotton-roll")


class MarketplaceApiTests(MarketplaceFactoryMixin, APITestCase):
    def _items(self, response):
        if isinstance(response.data, dict):
            return response.data.gt("results", response.data
        return response.data

    def test_storefront_create_assigns_authenticated_supplier(self):
        view = StorefrontViewSet.as_view({"post": "create"})
        request = self.factory.post(
            "/storefronts/",
            {"name": "Delta Mills", "country": "Egypt"},
            format="json",
        )
        force_authenticate(request, user=self.supplier)

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["supplier"], self.supplier.id)

    def test_products_are_publicly_listable(self):
        view = ProductViewSet.as_view({"get": "list"})
        request = self.factory.get("/products/")

        response = view(request)
        items = self._items(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(items[0]["name"], "Organic Cotton Roll")

    def test_saved_searches_are_scoped_to_authenticated_user(self):
        SavedSearch.objects.create(user=self.user, name="Cotton alerts", query="cotton")
        SavedSearch.objects.create(user=self.other_user, name="Silk alerts", query="silk")
        view = SavedSearchViewSet.as_view({"get": "list"})
        request = self.factory.get("/saved-searches/")
        force_authenticate(request, user=self.user)

        response = view(request)
        items = self._items(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Cotton alerts")

    def test_saved_product_create_assigns_authenticated_user(self):
        view = SavedProductViewSet.as_view({"post": "create"})
        request = self.factory.post(
            "/saved-products/",
            {"product": self.product.id, "notes": "Ask fore bulk discount"},
            format="json",
        )
        force_authenticate(request, user=self.user)

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            SavedProduct.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_favorite_supplier_model_supports_user_storefront_pairs(self):
        favorite = FavoriteSupplier.objects.create(
            user=self.user,
            storefront=self.storefront,
            notes="Reliable supplier",
        )

        self.assertEqual(str(favorite), f"{self.user} favorited {self.storefront}")


class MarketplaceUrlTests(TestCase):
    def test_router_exposes_core_marketplace_routes(self):
        route_names = {url.name for url in router.urls}

        expected = {
            "category-list",
            "certification-list",
            "storefront-list",
            "supplier-rating-list",
            "product-list",
            "variant-list",
            "document-list",
            "pricing-tier-list",
            "inventory-list",
            "shipping-option-list",
            "saved-search-list",
            "saved-product-list",
            "favorite-supplier-list",
            "review-list",
        }
        self.assertTrue(expected.issubset(route_names))
