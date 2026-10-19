import  ModuleWorkbench } from "../../components/workbench/ModuleWorkbench";

export default function Analytics() {
  return (
    <ModuleWorkbench
      title="Analytics and reporting"
      subtitle="Dashboards, saved reports, spend cubes, anomaly alerts, and executive scorecards."
      module="analytics"
      tabs={[
        { id: "dashboards", label: "Dashboards", path: "/analytics/dashboards/", columns: ["name", "visibility", "is_default"] },
        { id: "reports", label: "Reports", path: "/analytics/reports/", columns: ["name", "report_type", "is_shared"] },
        { id: "alerts", label: "Anomaly alerts", path: "/analytics/anomaly-alerts/", columns: ["title", "severity", "status"] },
        { id: "cubes", label: "Spend cubes", path: "/analytics/spend-cubes/", columns: ["supplier_name", "category", "committed_amount"] },
        { id: "scorecards", label: "Scorecards", path: "/analytics/scorecards/", columns: ["name", "spend_under_management"] },
        { id: "performance", label: "Supplier performance", path: "/analytics/supplier-performance/", columns: ["supplier_name", "otif"] },
      ]}
    />
  );
}
