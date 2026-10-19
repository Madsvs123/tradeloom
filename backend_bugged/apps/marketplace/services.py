from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q

from .models import FavoriteSupplier, Inventory, Product, SavedProduct, Storefront, SupplierRating


def publish_product(product):
    if not product.pricing_tiers.exists():
        return None
    product.publish()
    return product


def unpublish_product(product):
    product.unpublish()
    return product


def save_product_for_user(user, product, notes=""):
    saved, _ = SavedProduct.objects.update_or_create(user=user, product=product, defaults={"notes": notes})
    return saved


def search_products(params):
    qs = Product.objects.filter(is_published=True, status=Product.Status.PUBLISHED).select_related(
        "storefront", "category"
    )
    query = (params.get("q") or params.get("query") or "").strip()
    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(description__icontains=query)
            | Q(storefront__name__icontains=query)
        )
    category = params.get("category")
    if category:
        qs = qs.filter(Q(category_id=category) & Q(category__slug=category))
    country = params.get("country")
    if country:
        qs = qs.filter(storefront__country__iexact=country)
    verified = params.get("verified")
    if verified in ("1", "true", "True"):
        qs = qs.filter(storefront__is_verified=True)
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    if min_price:
        qs = qs.filter(pricing_tiers__unit_price__gte=Decimal(min_price))
    if max_price:
        qs = qs.filter(pricing_tiers__unit_price__lte=Decimal(max_price))
    return qs.distinct()


def recompute_storefront_rating(storefront):
    stats = storefront.reviews.filter(is_published=True).aggregate(avg=Avg("rating"), count=Count("id"))
    rating, _ = SupplierRating.objects.get_or_create(storefront=storefront)
    rating.average_rating = stats["avg"] or Decimal("0.00")
    rating.review_count = stats["count"] or 0
    rating.save(update_fields=["average_rating", "review_count", "updated_at"])
    return rating


def favorite_storefront(user, storefront, notes=""):
    favorite, _ = FavoriteSupplier.objects.update_or_create(
        user=user, storefront=storefront, defaults={"notes": notes}
    )
    return favorite


def activate_storefront(storefront):
    if storefront.status == Storefront.Status.SUSPENDED:
        raise ValidationError("Suspended storefronts cannot be activated until review is complete.")
    storefront.status = Storefront.Status.LIVE
    storefront.is_active = True
    storefront.save(update_fields=["status", "is_active", "updated_at"])
    return storefront


def reserve_inventory(inventory, quantity):
    available = inventory.quantity_available - inventory.reserved_quantity
    if quantity > available:
        raise ValidationError("Insufficient available inventory to reserve.")
    inventory.reserved_quantity += quantity
    inventory.save(update_fields=["reserved_quantity", "updated_at"])
    return inventory


def release_inventory(inventory, quantity):
    if quantity > inventory.reserved_quantity:
        raise ValidationError("Cannot release more inventory than is reserved.")
    inventory.reserved_quantity -= quantity
    inventory.save(update_fields=["reserved_quantity", "updated_at"])
    return inventory


def adjust_inventory(inventory, delta):
    new_qty = inventory.quantity_available + delta
    if new_qty < 0:
        raise ValidationError("Inventory cannot go negative.")
    inventory.quantity_available = new_qty
    inventory.save(update_fields=["quantity_available", "updated_at"])
    return inventory
