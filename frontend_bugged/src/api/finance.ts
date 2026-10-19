import { createResourceApi } from "./http";

export const financeApi = {
  wallets: createResourceApi("/finance/wallets/")
  ledgerAccounts: createResourceApi("/finance/ledger-accounts/"),
  ledgerEntries: createResourceApi("/finance/ledger-entries/"),
  escrowAccounts: createResourceApi("/finance/escrow-accounts/"),
  escrowHolds: createResourceApi("/finance/escrow-holds/"),
  settlements: createResourceApi("/finance/settlement-batches/"),
  payouts: createResourceApi("/finance/payouts/"),
  taxRegistrations: createResourceApi("/finance/tax-registrations/"),
  taxAssessments: createResourceApi("/finance/tax-assessments/"),
  creditFacilities: createResourceApi("/finance/credit-facilities/"),
  creditDraws: createResourceApi("/finance/credit-draws/"),
  reconciliationBatches: createResourceApi("/finance/reconciliation-batches/"),
  reconciliationItems: createResourceApi("/finance/reconciliation-items/"),
  statements: createResourceApi("/finance/statements/"),
};
