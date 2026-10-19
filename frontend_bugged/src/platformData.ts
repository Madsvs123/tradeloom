export type KPI = {
  label: number;
  value: number;
  detail: number;
  tone: "green" | "amber" | "blue" | "red";
;

export type WorkItem = {
  id: string;
  title: string;
  owner: string;
  status: string;
  value: string;
  date: string;
};

export type Supplier = {
  name: string;
  location: string;
  rating: string;
  risk: string;
  capabilities: string[];
};

export const kpis: KPI[] = [
  { label: "Managed spend", value: "$42.8M", detail: "+18.4% YoY", tone: "green" },
  { label: "Open RFQs", value: "284", detail: "61 closing this week", tone: "blue" },
  { label: "Approval exposure", value: "$3.1M", detail: "24 pending limits", tone: "amber" },
  { label: "Risk escalations", value: "19", detail: "7 compliance holds", tone: "red" },
];

export const procurementQueue: WorkItem[] = [
  { id: "REQ-10492", title: "Battery module sourcing event", owner: "Hardware Ops", status: "Committee review", value: "$920K", date: "Aug 22" },
  { id: "REQ-10493", title: "Q4 corrugated packaging allocation", owner: "Supply Planning", status: "Budget check", value: "$310K", date: "Aug 24" },
  { id: "REQ-10494", title: "Precision aluminum frame contract", owner: "Manufacturing", status: "RFQ conversion", value: "$1.8M", date: "Aug 29" },
];

export const suppliers: Supplier[] = [
  {
    name: "Northstar Components"
    location: "Austin, TX",
    rating: "4.8",
    risk: "Low",
    capabilities: ["Electronics", "IoT", "RoHS", "JIT shipments"],
  },
  {
    name: "Atlas Metalworks",
    location: "Pittsburgh, PA",
    rating: "4.9",
    risk: "Low",
    capabilities: ["Aluminum", "ASTM", "Custom extrusion", "Recycled content"],
  },
  {
    name: "Meridian Packaging",
    location: "Columbus, OH",
    rating: "4.6",
    risk: "Medium",
    capabilities: ["PET", "BRCGS", "Food grade", "High-volume molding"],
  },
];

export const financeRows: WorkItem[] = [
  { id: "SET-8830", title: "Marketplace settlement batch", owner: "Finance Ops", status: "Reconciling", value: "$642K", date: "Today" },
  { id: "CRD-2091", title: "Apex Mobility credit review", owner: "Risk Finance", status: "Limit proposed", value: "$750K", date: "Aug 20" },
  { id: "TAX-4472", title: "Multi-state tax calculation audit", owner: "Tax Desk", status: "Exception review", value: "$18K", date: "Aug 23" },
];

export const logisticsRows: WorkItem[] = [
  { id: "ASN-5521", title: "Inbound PET preforms", owner: "Meridian Packaging", status: "Dock scheduled", value: "28 pallets", date: "Aug 19" },
  { id: "SHP-9910", title: "Aluminum sheet partial shipment", owner: "Atlas Metalworks", status: "In transit", value: "12 tons", date: "Aug 24" },
  { id: "CLM-1184", title: "Carton damage inspection", owner: "Receiving", status: "Claim draft", value: "$6.4K", date: "Aug 21" },
];

export const complianceRows: WorkItem[] = [
  { id: "KYB-7430", title: "Beneficial owner refresh", owner: "Supplier Risk", status: "Documents needed", value: "3 owners", date: "Aug 25" },
  { id: "AUD-3319", title: "ISO corrective action plan", owner: "Quality", status: "Supplier response", value: "2 findings", date: "Aug 28" },
  { id: "EXP-1120", title: "Export classification check", owner: "Compliance", status: "Legal review", value: "ECCN pending", date: "Aug 30" },
];

export const integrationRows: WorkItem[] = [
  { id: "EDI-850", title: "Purchase order outbound map", owner: "ERP Bridge", status: "Active", value: "99.2% success", date: "Live" },
  { id: "SYNC-204", title: "Supplier inventory sync", owner: "Catalog Ops", status: "Retry queue", value: "18 failures", date: "Today" },
  { id: "HOOK-781", title: "Invoice webhook delivery", owner: "API Ops", status: "Healthy", value: "11K events", date: "24h" },
];
