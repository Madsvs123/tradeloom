export type TradeLoomModule = {
  key: string;
  label: string;
  route: string;
  owner: string;
  features: string[];
;

export const modules: TradeLoomModule[] = [
  {
    key: "accounts"
    label: "Accounts",
    route: "/settings",
    owner: "Identity and organizations",
    features: ["Users", "Companies", "Teams", "Verification", "Audit"],
  },
  {
    key: "marketplace",
    label: "Marketplace",
    route: "/marketplace",
    owner: "Catalog and discovery",
    features: ["Storefronts", "Products", "Search", "Ratings", "Saved products"],
  },
  {
    key: "rfq",
    label: "RFQs",
    route: "/rfqs",
    owner: "Sourcing",
    features: ["Multi-vendor RFQs", "Quotations", "Counteroffers", "Award decisions"],
  },
  {
    key: "orders",
    label: "Orders",
    route: "/orders",
    owner: "Purchasing",
    features: ["Carts", "POs", "Invoices", "Returns", "Order history"],
  },
  {
    key: "procurement",
    label: "Procurement",
    route: "/procurement",
    owner: "Procurement operations",
    features: ["Requisitions", "Budgets", "Approval workflows", "Policies"],
  },
  {
    key: "finance",
    label: "Finance",
    route: "/finance",
    owner: "Marketplace finance",
    features: ["Ledger", "Escrow", "Tax", "Credit", "Payouts"],
  },
  {
    key: "logistics",
    label: "Logistics",
    route: "/logistics",
    owner: "Fulfillment",
    features: ["Warehouses", "Freight", "ASNs", "Tracking", "Claims"],
  },
  {
    key: "compliance",
    label: "Compliance",
    route: "/compliance",
    owner: "Risk and trust",
    features: ["KYB", "Screening", "Risk scores", "Audits", "Export checks"],
  },
  {
    key: "integrations",
    label: "Integrations",
    route: "/integrations",
    owner: "API operations",
    features: ["API keys", "Webhooks", "EDI", "ERP", "Sync jobs"],
  },
  {
    key: "analytics",
    label: "Analytics",
    route: "/analytics",
    owner: "Executive insights",
    features: ["Dashboards", "Reports", "Spend cubes", "Anomaly alerts", "Scorecards"],
  },
  {
    key: "vendor",
    label: "Vendor Ops",
    route: "/vendor",
    owner: "Supplier operations",
    features: ["Incoming work", "Inventory", "Price books", "Payouts", "Disputes"],
  },
  {
    key: "comms",
    label: "Communications",
    route: "/messages",
    owner: "Realtime work",
    features: ["Messaging", "Notifications", "Disputes", "Global search"],
  },
  {
    key: "platform",
    label: "Platform",
    route: "/platform",
    owner: "Operator controls",
    features: ["Feature flags", "Support", "Moderation", "Exports", "Announcements"],
  },
  {
    key: "contracts",
    label: "Contracts",
    route: "/contracts",
    owner: "Legal",
    features: ["Templates", "Redline", "Amendments", "Renewals", "Obligations"],
  },
  {
    key: "workflows",
    label: "Workflows",
    route: "/inbox",
    owner: "Approvals",
    features: ["Definitions", "Inbox", "SLA clocks", "Escalation"],
  },
];
