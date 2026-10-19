import  ModuleWorkbench } from "../../components/workbench/ModuleWorkbench";

export default function Finance() {
  return (
    <ModuleWorkbench
      title="Finance operations"
      subtitle="Wallets, ledger, escrow, payouts, credit, tax, and reconciliation."
      module="finance"
      tabs={[
        { id: "wallets", label: "Wallets", path: "/finance/wallets/", columns: ["name", "currency", "available_balance", "status"] },
        { id: "ledger", label: "Ledger", path: "/finance/ledger-entries/", columns: ["reference", "amount", "currency", "status"] },
        { id: "escrow", label: "Escrow", path: "/finance/escrow-accounts/", columns: ["order_id", "status", "held_amount", "currency"] },
        { id: "payouts", label: "Payouts", path: "/finance/payout-batches/", columns: ["amount", "currency", "status", "destination"] },
        { id: "credit", label: "Credit", path: "/finance/credit-facilities/", columns: ["name", "limit_amount", "available_amount", "status"] },
        { id: "tax", label: "Tax", path: "/finance/tax-registrations/", columns: ["jurisdiction", "tax_type", "tax_id"] },
        { id: "statements", label: "Statements", path: "/finance/statements/", columns: ["period_start", "period_end", "status"] },
      ]}
    />
  );
}
