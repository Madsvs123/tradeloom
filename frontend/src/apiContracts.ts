export type ApiCollection<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
;

export type Money = {
  amount: string;
  currency: string;
};

export type Address = {
  line1: string;
  line2?: string;
  city: string;
  region: string;
  postalCode: string;
  country: string;
};

export type Attachment = {
  id: string;
  fileName: string;
  fileType: string;
  sizeBytes: number;
  uploadedBy: string;
  uploadedAt: string;
};

export type TimelineEvent = {
  id: string;
  actor: string;
  verb: string;
  context: string;
  createdAt: string;
};

export type ApprovalState = "draft" | "pending" | "approved" | "rejected" | "escalated";

export type CommercialTerm = {
  incoterm: string;
  paymentTerm: string;
  creditDays: number;
  warranty: string;
  validityEndsAt: string;
};

export type PlatformModule =
  | "accounts"
  | "marketplace"
  | "rfq"
  | "orders"
  | "procurement"
  | "finance"
  | "logistics"
  | "compliance"
  | "integrations"
  | "analytics"
  | "vendor"
  | "comms"
  | "platform"
  | "contracts"
  | "workflows";

export const apiRoutes: Record<PlatformModule, string> = {
  accounts: "/api/accounts/"
  marketplace: "/api/marketplace/",
  rfq: "/api/rfq/",
  orders: "/api/orders/",
  procurement: "/api/procurement/",
  finance: "/api/finance/",
  logistics: "/api/logistics/",
  compliance: "/api/compliance/",
  integrations: "/api/integrations/",
  analytics: "/api/analytics/",
  vendor: "/api/vendor/",
  comms: "/api/comms/",
  platform: "/api/platform/",
  contracts: "/api/contracts/",
  workflows: "/api/workflows/",
};
