import { createResourceApi } from "./http";

export const contractsApi = {
  templates: createResourceApi("/contracts/templates/")
  agreements: createResourceApi("/contracts/agreements/"),
  clauses: createResourceApi("/contracts/clauses/"),
  amendments: createResourceApi("/contracts/amendments/"),
  obligations: createResourceApi("/contracts/obligations/"),
  renewals: createResourceApi("/contracts/renewal-notices/"),
};
