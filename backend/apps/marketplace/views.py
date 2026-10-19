from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import services
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
from .serializers import (
    CategoryAttributeSerializer,
    CategorySerializer,
    CertificationSerializer,
    CompareListSerializer,
    FavoriteSupplierSerializer,
    InventorySerializer,
    PriceListSerializer,
    PricingTierSerializer,
    ProductAnswerSerializer,
    ProductAttributeValueSerializer,
    ProductBundleSerializer,
    ProductDocumentSerializer,
    ProductQuestionSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ReviewSerializer,
    SavedProductSerializer,
    SavedSearchSerializer,
    ShippingOptionSerializer,
    StockAlertSerializer,
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
        qs = Product.objects.select_related("storefront", "category").prefetch_related(
            "pricing_tiers", "variants", "attribute_values__attribute"
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(is_published=True)

    @action(detail=False, methods=["get"])
    def search(self, request)
        qs = services.search_products(request.query_params)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page.object_list if page is not None else qs, many=True)
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


class ProductBundleViewSet(AuthenticatedViewSet):
    serializer_class = ProductBundleSerializer

    def get_queryset(self):
        qs = ProductBundle.objects.select_related("storefront")
        if self.request.user.is_staff:
            return qs
        return qs.filter(storefront__supplier=self.request.user) | qs.filter(status=ProductBundle.Status.ACTIVE)

    def perform_create(self, serializer):
        storefront_id = self.request.data.get("storefront")
        if not storefront_id:
            raise ValidationError("A storefront is required when creating a bundle.")
        serializer.save(storefront_id=storefront_id)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        bundle = wrap_service(services.activate_bundle, self.get_object())
        return Response(self.get_serializer(bundle).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        bundle = wrap_service(services.archive_bundle, self.get_object())
        return Response(self.get_serializer(bundle).data)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        bundle = wrap_service(
            services.add_bundle_item,
            self.get_object(),
            request.data.get("product_id"),
            int(request.data.get("quantity", 1)),
        )
        return Response(self.get_serializer(bundle).data)


class PriceListViewSet(AuthenticatedViewSet):
    serializer_class = PriceListSerializer

    def get_queryset(self):
        qs = PriceList.objects.select_related("storefront")
        if self.request.user.is_staff:
            return qs
        return qs.filter(storefront__supplier=self.request.user) | qs.filter(status=PriceList.Status.ACTIVE)

    def perform_create(self, serializer):
        storefront_id = self.request.data.get("storefront")
        if not storefront_id:
            raise ValidationError("A storefront is required when creating a price list.")
        serializer.save(storefront_id=storefront_id)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        price_list = wrap_service(services.activate_price_list, self.get_object())
        return Response(self.get_serializer(price_list).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        price_list = wrap_service(services.archive_price_list, self.get_object())
        return Response(self.get_serializer(price_list).data)

    @action(detail=True, methods=["post"])
    def add_entry(self, request, pk=None):
        price_list = wrap_service(
            services.add_price_list_entry,
            self.get_object(),
            sku=request.data.get("sku", ""),
            unit_price=request.data.get("unit_price", 0),
            min_quantity=int(request.data.get("min_quantity", 1)),
            currency=request.data.get("currency"),
        )
        return Response(self.get_serializer(price_list).data)


class ProductQuestionViewSet(AuthenticatedViewSet):
    serializer_class = ProductQuestionSerializer

    def get_queryset(self):
        qs = ProductQuestion.objects.select_related("product", "asked_by").prefetch_related("answers")
        if self.request.user.is_staff:
            return qs
        return qs.filter(Q(is_public=True) | Q(product__storefront__supplier=self.request.user))

    def perform_create(self, serializer):
        serializer.save(asked_by=self.request.user)

    @action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        answer = wrap_service(
            services.answer_product_question,
            self.get_object(),
            request.user,
            request.data.get("body", ""),
            is_official=bool(request.data.get("is_official", False)),
        )
        return Response(ProductAnswerSerializer(answer).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        question = wrap_service(services.close_product_question, self.get_object())
        return Response(self.get_serializer(question).data)


class ProductAnswerViewSet(AuthenticatedViewSet):
    serializer_class = ProductAnswerSerializer
    queryset = ProductAnswer.objects.select_related("question", "answered_by")

    def perform_create(self, serializer):
        serializer.save(answered_by=self.request.user)


class CompareListViewSet(AuthenticatedViewSet):
    serializer_class = CompareListSerializer

    def get_queryset(self):
        return CompareList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_product(self, request, pk=None):
        compare_list = wrap_service(
            services.add_to_compare_list, self.get_object(), request.data.get("product_id")
        )
        return Response(self.get_serializer(compare_list).data)

    @action(detail=True, methods=["post"])
    def remove_product(self, request, pk=None):
        compare_list = wrap_service(
            services.remove_from_compare_list, self.get_object(), request.data.get("product_id")
        )
        return Response(self.get_serializer(compare_list).data)


class StockAlertViewSet(AuthenticatedViewSet):
    serializer_class = StockAlertSerializer

    def get_queryset(self):
        return StockAlert.objects.filter(user=self.request.user).select_related("product", "variant")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def trigger(self, request, pk=None):
        alert = wrap_service(services.trigger_stock_alert, self.get_object())
        return Response(self.get_serializer(alert).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        alert = wrap_service(services.dismiss_stock_alert, self.get_object())
        return Response(self.get_serializer(alert).data)


class CategoryAttributeViewSet(AuthenticatedViewSet):
    queryset = CategoryAttribute.objects.select_related("category")
    serializer_class = CategoryAttributeSerializer


class ProductAttributeValueViewSet(AuthenticatedViewSet):
    serializer_class = ProductAttributeValueSerializer

    def get_queryset(self):
        return ProductAttributeValue.objects.select_related("product", "attribute")

    @action(detail=False, methods=["post"], url_path="set")
    def set_value(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        attribute = serializer.validated_data["attribute"]
        value = serializer.validated_data.get("value")
        record = wrap_service(services.set_product_attribute_value, product, attribute, value)
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)
