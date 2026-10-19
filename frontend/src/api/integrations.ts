import { createResourceApi  from "./http";

export const integrationsApi = {
  clients: createResourceApi("/integrations/api-clients/"),
  keys: createResourceApi("/integrations/api-keys/"),
  retryPolicies: createResourceApi("/integrations/retry-policies/"),
  webhooks: createResourceApi("/integrations/webhook-endpoints/"),
  subscriptions: createResourceApi("/integrations/webhook-subscriptions/"),
  deliveries: createResourceApi("/integrations/webhook-deliveries/"),
  ediPartners: createResourceApi("/integrations/edi-partners/"),
  ediDocuments: createResourceApi("/integrations/edi-documents/"),
  erp: createResourceApi("/integrations/erp-connectors/"),
  sftp: createResourceApi("/integrations/sftp-dropboxes/"),
  mappings: createResourceApi("/integrations/mapping-templates/"),
  catalogImports: createResourceApi("/integrations/catalog-import-jobs/"),
  priceSync: createResourceApi("/integrations/price-sync-jobs/"),
  inventorySync: createResourceApi("/integrations/inventory-sync-jobs/"),
  automations: createResourceApi("/integrations/automation-rules/"),
  events: createResourceApi("/integrations/integration-events/"),
  deadLetters: createResourceApi("/integrations/dead-letter-records/"),
};
