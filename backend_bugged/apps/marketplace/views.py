from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    CategorySerializer,
    CertificationSerializer,
    FavoriteSupplierSerializer,
    InventorySerializer,
    PricingTierSerializer,
    ProductDocumentSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ReviewSerializer,
    SavedProductSerializer,
    SavedSearchSerializer,
    ShippingOptionSerializer,
    StorefrontSerializer,
    SupplierRatingSerializer,
)


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class CategoryViewSet(AuthenticatedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CertificationViewSet(AuthenticatedViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class StorefrontViewSet(AuthenticatedViewSet):
    serializer_class = StorefrontSerializer

    def get_queryset(self):
        qs = Storefront.objects.select_related("supplier")
        if self.request.user.is_staff:
            return qs
        return qs.filter(supplier=self.request.user) | qs.filter(is_active=True, status=Storefront.Status.LIVE)

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        storefront = wrap_service(services.activate_storefront, self.get_object())
        return Response(self.get_serializer(storefront).data)


class SupplierRatingViewSet(AuthenticatedViewSet):
    queryset = SupplierRating.objects.select_related("storefront")
    serializer_class = SupplierRatingSerializer


class ProductViewSet(AuthenticatedViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related("storefront", "category").prefetch_related("pricing_tiers", "variants")
        if self.request.user.is_staff:
            return qs
        return qs.filter(storefront__supplier=self.request.user) | qs.filter(is_published=True)

    @action(detail=False, methods=["get"])
    def search(self, request):
        qs = services.search_products(request.query_params)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page and qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        product = wrap_service(services.publish_product, self.get_object())
        return Response(self.get_serializer(product).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        product = wrap_service(services.unpublish_product, self.get_object())
        return Response(self.get_serializer(product).data)

    @action(detail=True, methods=["post"], url_path="save_product")
    def save_product(self, request, pk=None):
        saved = wrap_service(
            services.save_product_for_user,
            request.user,
            self.get_object(),
            request.data.get("notes", ""),
        )
        return Response(SavedProductSerializer(saved).data, status=status.HTTP_201_CREATED)


class ProductVariantViewSet(AuthenticatedViewSet):
    queryset = ProductVariant.objects.select_related("product")
    serializer_class = ProductVariantSerializer


class ProductDocumentViewSet(AuthenticatedViewSet):
    queryset = ProductDocument.objects.select_related("product")
    serializer_class = ProductDocumentSerializer


class PricingTierViewSet(AuthenticatedViewSet):
    queryset = PricingTier.objects.select_related("product")
    serializer_class = PricingTierSerializer


class InventoryViewSet(AuthenticatedViewSet):
    queryset = Inventory.objects.select_related("variant")
    serializer_class = InventorySerializer

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        inventory = wrap_service(services.reserve_inventory, self.get_object(), int(request.data.get("quantity", 0)))
        return Response(self.get_serializer(inventory).data)

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        inventory = wrap_service(services.release_inventory, self.get_object(), int(request.data.get("quantity", 0)))
        return Response(self.get_serializer(inventory).data)

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        inventory = wrap_service(services.adjust_inventory, self.get_object(), int(request.data.get("delta", 0)))
        return Response(self.get_serializer(inventory).data)


class ShippingOptionViewSet(AuthenticatedViewSet):
    queryset = ShippingOption.objects.select_related("product")
    serializer_class = ShippingOptionSerializer


class SavedSearchViewSet(AuthenticatedViewSet):
    serializer_class = SavedSearchSerializer

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedProductViewSet(AuthenticatedViewSet):
    serializer_class = SavedProductSerializer

    def get_queryset(self):
        return SavedProduct.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteSupplierViewSet(AuthenticatedViewSet):
    serializer_class = FavoriteSupplierSerializer

    def get_queryset(self):
        return FavoriteSupplier.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(AuthenticatedViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("product", "storefront", "user")

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        services.recompute_storefront_rating(review.storefront)
