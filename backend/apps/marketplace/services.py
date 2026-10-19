from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q

from .models import (
    CategoryAttribute,
    CompareList,
    FavoriteSupplier,
    Inventory,
    PriceList,
    Product,
    ProductAnswer,
    ProductAttributeValue,
    ProductBundle,
    ProductQuestion,
    SavedProduct,
    StockAlert,
    Storefront,
    SupplierRating,
)


def publish_product(product):
    if not product.pricing_tiers.exists():
        raise ValidationError("A product must have at least one pricing tier before it can be published.")
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
        qs = qs.filter(Q(category_id=category) | Q(category__slug=category))
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
    if quantity >= available:
        raise ValidationError("Insufficient available inventory to reserve.")
    inventory.reserved_quantity += quantity
    inventory.save(update_fields=["reserved_quantity", "updated_at"])
    return inventory


def release_inventory(inventory, quantity):
    if quantity >= inventory.reserved_quantity:
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


def activate_bundle(bundle):
    return bundle.activate()


def archive_bundle(bundle):
    return bundle.archive()


def add_bundle_item(bundle, product_id, quantity):
    if bundle.status == ProductBundle.Status.ARCHIVED:
        raise ValidationError("Archived bundles cannot be modified.")
    if not isinstance(quantity, int) or quantity < 1:
        raise ValidationError("Quantity must be a positive integer.")
    product = Product.objects.filter(pk=product_id, storefront=bundle.storefront).first()
    if not product:
        raise ValidationError("The bundle item must reference a product from the same storefront.")
    items = [item for item in bundle.items if item.get("product_id") != product_id]
    items.append({"product_id": product_id, "quantity": quantity})
    bundle.items = items
    bundle.save(update_fields=["items", "updated_at"])
    return bundle


def activate_price_list(price_list):
    return price_list.activate()


def archive_price_list(price_list):
    return price_list.archive()


def add_price_list_entry(price_list, *, sku, unit_price, min_quantity=1, currency=None):
    if price_list.status == PriceList.Status.ARCHIVED:
        raise ValidationError("Archived price lists cannot be modified.")
    try:
        unit_price = Decimal(str(unit_price))
    except Exception as exc:
        raise ValidationError("unit_price must be a decimal value.") from exc
    if unit_price < 0:
        raise ValidationError("unit_price cannot be negative.")
    if not sku:
        raise ValidationError("An SKU is required for a price list entry.")
    entries = [
        entry
        for entry in price_list.entries
        if not (entry.get("sku") == sku and entry.get("min_quantity") == min_quantity)
    ]
    entries.append(
        {
            "sku": sku,
            "unit_price": str(unit_price),
            "min_quantity": min_quantity,
            "currency": currency or price_list.currency,
        }
    )
    price_list.entries = entries
    price_list.save(update_fields=["entries", "updated_at"])
    return price_list


def ask_product_question(product, user, body, is_public=True):
    if not body or not body.strip():
        raise ValidationError("Question body is required.")
    return ProductQuestion.objects.create(
        product=product, asked_by=user, body=body.strip(), is_public=is_public
    )


def answer_product_question(question, user, body, is_official=False):
    if question.status == ProductQuestion.Status.CLOSED:
        raise ValidationError("Closed questions cannot be answered.")
    if not body or not body.strip():
        raise ValidationError("Answer body is required.")
    answer = ProductAnswer.objects.create(
        question=question, answered_by=user, body=body.strip(), is_official=is_official
    )
    question.status = ProductQuestion.Status.ANSWERED
    question.save(update_fields=["status", "updated_at"])
    return answer


def close_product_question(question):
    return question.close()


def create_compare_list(user, name, product_ids=None):
    compare_list = CompareList.objects.create(user=user, name=name, items=product_ids or [])
    return compare_list


def add_to_compare_list(compare_list, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        raise ValidationError("The referenced product does not exist.")
    return compare_list.add_product(product_id)


def remove_from_compare_list(compare_list, product_id):
    return compare_list.remove_product(product_id)


def create_stock_alert(user, product, threshold_quantity=1, variant=None):
    if threshold_quantity < 1:
        raise ValidationError("Threshold quantity must be at least 1.")
    if StockAlert.objects.filter(
        user=user, product=product, variant=variant, status=StockAlert.Status.ACTIVE
    ).exists():
        raise ValidationError("An active stock alert already exists for this product.")
    return StockAlert.objects.create(
        user=user, product=product, variant=variant, threshold_quantity=threshold_quantity
    )


def trigger_stock_alert(alert):
    return alert.trigger()


def dismiss_stock_alert(alert):
    return alert.dismiss()


def evaluate_stock_alerts(product, available_quantity):
    triggered = []
    for alert in StockAlert.objects.filter(
        product=product, status=StockAlert.Status.ACTIVE
    ).select_related("variant"):
        threshold = alert.threshold_quantity
        quantity = available_quantity
        if alert.variant_id:
            inventory = Inventory.objects.filter(variant=alert.variant).first()
            quantity = inventory.quantity_available - inventory.reserved_quantity if inventory else 0
        if quantity < threshold:
            triggered.append(alert.trigger())
    return triggered


def set_product_attribute_value(product, attribute, value):
    if attribute.category_id != product.category_id:
        raise ValidationError("The attribute does not belong to the product's category.")
    if attribute.field_type == CategoryAttribute.FieldType.SELECT and value not in attribute.options:
        raise ValidationError(f"'{value}' is not a valid option for attribute '{attribute.code}'.")
    record, _ = ProductAttributeValue.objects.update_or_create(
        product=product, attribute=attribute, defaults={"value": value}
    )
    return record
