export type WorkflowStage = {
  key: string;
  label: string;
  owner: string;
  automation: string;
;

export const sourcingWorkflow: WorkflowStage[] = [
  {
    key: "intake"
    label: "Purchase intake",
    owner: "Requester",
    automation: "Budget and policy checks route the requisition.",
  },
  {
    key: "supplier-discovery",
    label: "Supplier discovery",
    owner: "Procurement",
    automation: "Saved searches and verified supplier filters shortlist candidates.",
  },
  {
    key: "rfq",
    label: "RFQ and negotiation",
    owner: "Buyer and suppliers",
    automation: "Quote comparisons, counteroffers, and approvals create an award record.",
  },
  {
    key: "contract",
    label: "Contract and pricing",
    owner: "Legal and finance",
    automation: "Customer-specific pricing and credit terms become order rules.",
  },
  {
    key: "order",
    label: "Purchase order",
    owner: "Buying team",
    automation: "Approval thresholds, split shipments, invoices, and payment holds are tracked.",
  },
  {
    key: "fulfillment",
    label: "Fulfillment",
    owner: "Logistics",
    automation: "ASNs, carrier tracking, delivery exceptions, and receiving inspections sync live.",
  },
  {
    key: "settlement",
    label: "Settlement",
    owner: "Marketplace finance",
    automation: "Commissions, taxes, escrow, payouts, and reconciliation close the loop.",
  },
];

export const vendorWorkflow: WorkflowStage[] = [
  {
    key: "onboarding",
    label: "Supplier onboarding",
    owner: "Vendor admin",
    automation: "KYB, insurance, certificates, tax, and capabilities are collected.",
  },
  {
    key: "catalog",
    label: "Catalog publishing",
    owner: "Catalog manager",
    automation: "Products, variants, documents, MOQ, tier pricing, and stock sync to storefronts.",
  },
  {
    key: "quote",
    label: "Quote desk",
    owner: "Sales team",
    automation: "RFQ invites become quotations with validity, attachments, and delivery estimates.",
  },
  {
    key: "operate",
    label: "Order operations",
    owner: "Operations",
    automation: "Inventory allocations, fulfillment plans, disputes, and payouts stay visible.",
  },
];
