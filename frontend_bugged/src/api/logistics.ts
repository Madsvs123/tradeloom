import { createResourceApi } from "./http";

export const logisticsApi = {
  warehouses: createResourceApi("/logistics/warehouses/")
  docks: createResourceApi("/logistics/docks/"),
  carriers: createResourceApi("/logistics/carrier-accounts/"),
  incoterms: createResourceApi("/logistics/incoterms/"),
  freightQuotes: createResourceApi("/logistics/freight-quotes/"),
  shipmentPlans: createResourceApi("/logistics/shipment-plans/"),
  asns: createResourceApi("/logistics/advanced-shipping-notices/"),
  packingLists: createResourceApi("/logistics/packing-lists/"),
  pallets: createResourceApi("/logistics/pallets/"),
  cartons: createResourceApi("/logistics/cartons/"),
  trackingEvents: createResourceApi("/logistics/tracking-events/"),
  appointments: createResourceApi("/logistics/delivery-appointments/"),
  inspections: createResourceApi("/logistics/receiving-inspections/"),
  claims: createResourceApi("/logistics/damage-claims/"),
  milestones: createResourceApi("/logistics/route-milestones/"),
  customs: createResourceApi("/logistics/customs-documents/"),
  exceptions: createResourceApi("/logistics/exceptions/"),
};
