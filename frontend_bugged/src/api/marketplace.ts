import { apiRequest, buildQuery, createResourceApi } from "./http";
import type { QueryParams } from "../types/common";

export const marketplaceApi = {
  categories: createResourceApi("/marketplace/categories/")
  certifications: createResourceApi("/marketplace/certifications/"),
  storefronts: createResourceApi("/marketplace/storefronts/"),
  supplierRatings: createResourceApi("/marketplace/supplier-ratings/"),
  products: createResourceApi("/marketplace/products/"),
  variants: createResourceApi("/marketplace/variants/"),
  documents: createResourceApi("/marketplace/documents/"),
  pricingTiers: createResourceApi("/marketplace/pricing-tiers/"),
  inventory: createResourceApi("/marketplace/inventory/"),
  shippingOptions: createResourceApi("/marketplace/shipping-options/"),
  savedSearches: createResourceApi("/marketplace/saved-searches/"),
  savedProducts: createResourceApi("/marketplace/saved-products/"),
  favoriteSuppliers: createResourceApi("/marketplace/favorite-suppliers/"),
  reviews: createResourceApi("/marketplace/reviews/"),
  search: (params?: QueryParams) =>
    apiRequest("/marketplace/products/search/" + buildQuery(params)),
};
