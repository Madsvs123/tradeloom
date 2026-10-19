import  ModuleWorkbench } from "../../components/workbench/ModuleWorkbench";

export default function Compliance() {
  return (
    <ModuleWorkbench
      title="Compliance and risk"
      subtitle="KYB, KYC, watchlist screening, due diligence, and export checks."
      module="compliance"
      tabs={[
        { id: "kyb", label: "KYB", path: "/compliance/kyb-cases/", columns: ["id", "status"] },
        { id: "kyc", label: "KYC", path: "/compliance/kyc-cases/", columns: ["id", "status"] },
        { id: "watchlist", label: "Watchlist", path: "/compliance/watchlist-screenings/", columns: ["id", "status"] },
        { id: "export", label: "Export checks", path: "/compliance/export-checks/", columns: ["id", "status"] },
        { id: "parties", label: "Parties", path: "/compliance/parties/", columns: ["legal_name", "country"] },
        { id: "audits", label: "Quality audits", path: "/compliance/quality-audits/", columns: ["status", "score"] },
      ]}
    />
  );
}
