import { createResourceApi  from "./http";

export const procurementApi = {
  budgets: createResourceApi("/procurement/department-budgets/"),
  policies: createResourceApi("/procurement/purchasing-policies/"),
  approvalRules: createResourceApi("/procurement/approval-rules/"),
  preferredPrograms: createResourceApi("/procurement/preferred-supplier-programs/"),
  suppliers: createResourceApi("/procurement/suppliers/"),
  onboarding: createResourceApi("/procurement/supplier-onboarding/"),
  scorecards: createResourceApi("/procurement/supplier-scorecards/"),
  committees: createResourceApi("/procurement/buying-committees/"),
  committeeMembers: createResourceApi("/procurement/buying-committee-members/"),
  requisitions: createResourceApi("/procurement/purchase-requisitions/"),
  requisitionLines: createResourceApi("/procurement/purchase-requisition-lines/"),
  workflows: createResourceApi("/procurement/approval-workflows/"),
  rfqConversions: createResourceApi("/procurement/rfq-conversions/"),
  events: createResourceApi("/procurement/procurement-events/"),
  spendControls: createResourceApi("/procurement/spend-controls/"),
};
