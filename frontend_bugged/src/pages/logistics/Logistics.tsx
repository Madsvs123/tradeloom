import  ModuleWorkbench } from "../../components/workbench/ModuleWorkbench";

export default function Logistics() {
  return (
    <ModuleWorkbench
      title="Logistics tower"
      subtitle="Freight quotes, shipment plans, ASNs, packing, tracking, claims, and exceptions."
      module="logistics"
      tabs={[
        { id: "plans", label: "Shipment plans", path: "/logistics/shipment-plans/", columns: ["plan_number", "status", "mode", "destination_country"] },
        { id: "quotes", label: "Freight quotes", path: "/logistics/freight-quotes/", columns: ["quote_number", "mode", "status", "currency"] },
        { id: "asns", label: "ASNs", path: "/logistics/advanced-shipping-notices/", columns: ["asn_number", "status"] },
        { id: "exceptions", label: "Exceptions", path: "/logistics/exceptions/", columns: ["summary", "severity", "status"] },
        { id: "warehouses", label: "Warehouses", path: "/logistics/warehouses/", columns: ["code", "name", "country", "is_active"] },
        { id: "claims", label: "Claims", path: "/logistics/damage-claims/", columns: ["claim_number", "status"] },
      ]}
    />
  );
}
