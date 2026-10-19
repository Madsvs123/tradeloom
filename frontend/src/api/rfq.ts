import { createResourceApi  from "./http";

export const rfqApi = {
  rfqs: createResourceApi("/rfq/rfqs/"),
  quotations: createResourceApi("/rfq/quotations/"),
  messages: createResourceApi("/rfq/messages/"),
  counteroffers: createResourceApi("/rfq/counteroffers/"),
  attachments: createResourceApi("/rfq/attachments/"),
};
