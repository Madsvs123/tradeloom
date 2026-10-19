import  ModuleWorkbench } from "../../components/workbench/ModuleWorkbench";

export default function Integrations() {
  return (
    <ModuleWorkbench
      title="Integration hub"
      subtitle="API clients, webhooks, EDI, ERP connectors, and catalog sync jobs."
      module="integrations"
      tabs={[
        { id: "clients", label: "API clients", path: "/integrations/api-clients/", columns: ["name", "status"] },
        { id: "webhooks", label: "Webhooks", path: "/integrations/webhook-endpoints/", columns: ["url", "status"] },
        { id: "erp", label: "ERP connectors", path: "/integrations/erp-connectors/", columns: ["name", "status"] },
        { id: "edi", label: "EDI partners", path: "/integrations/edi/", columns: ["name", "status"] },
        { id: "dead", label: "Dead letters", path: "/integrations/dead-letter-records/", columns: ["reason", "status"] },
        { id: "imports", label: "Catalog imports", path: "/integrations/catalog-import-jobs/", columns: ["id", "status"] },
      ]}
    />
  );
}
