import { createResourceApi } from "./http";

export const complianceApi = {
  parties: createResourceApi("/compliance/parties/")
  riskScores: createResourceApi("/compliance/risk-scores/"),
  kyb: createResourceApi("/compliance/kyb-cases/"),
  kyc: createResourceApi("/compliance/kyc-cases/"),
  beneficialOwners: createResourceApi("/compliance/beneficial-owners/"),
  diligence: createResourceApi("/compliance/supplier-due-diligence/"),
  documents: createResourceApi("/compliance/documents/"),
  screenings: createResourceApi("/compliance/watchlist-screenings/"),
  policies: createResourceApi("/compliance/policies/"),
  taxForms: createResourceApi("/compliance/tax-forms/"),
  insurance: createResourceApi("/compliance/insurance/"),
  audits: createResourceApi("/compliance/quality-audits/"),
  correctiveActions: createResourceApi("/compliance/corrective-actions/"),
  incidents: createResourceApi("/compliance/incidents/"),
  retention: createResourceApi("/compliance/data-retention-requests/"),
  exportChecks: createResourceApi("/compliance/export-checks/"),
};
