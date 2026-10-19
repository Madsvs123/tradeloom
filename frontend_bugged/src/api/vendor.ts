import { apiRequest, buildQuery, createResourceApi } from "./http";
import type { QueryParams } from "../types/common";

export const vendorApi = {
  vendors: createResourceApi("/vendor/vendors/")
  team: createResourceApi("/vendor/team-memberships/"),
  inventoryItems: createResourceApi("/vendor/inventory/items/"),
  inventoryAdjustments: createResourceApi("/vendor/inventory/adjustments/"),
  priceBook: createResourceApi("/vendor/price-book/items/"),
  priceChanges: createResourceApi("/vendor/price-book/changes/"),
  orders: createResourceApi("/vendor/orders/"),
  rfqs: createResourceApi("/vendor/rfqs/"),
  notes: createResourceApi("/vendor/customer-notes/"),
  payouts: createResourceApi("/vendor/payouts/"),
  disputes: createResourceApi("/vendor/disputes/"),
  reports: createResourceApi("/vendor/reports/"),
  incomingWork: (params?: QueryParams) =>
    apiRequest(`/vendor/dashboards/incoming-work/${buildQuery(params)}`),
  inventoryDashboard: (params?: QueryParams) =>
    apiRequest(`/vendor/dashboards/inventory/${buildQuery(params)}`),
  payoutDashboard: (params?: QueryParams) =>
    apiRequest(`/vendor/dashboards/payouts/${buildQuery(params)}`),
  disputeDashboard: (params?: QueryParams) =>
    apiRequest(`/vendor/dashboards/disputes/${buildQuery(params)}`),
  sales: (params?: QueryParams) => apiRequest(`/vendor/analytics/sales/${buildQuery(params)}`),
};
