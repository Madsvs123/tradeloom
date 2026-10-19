import { apiRequest, buildQuery, createResourceApi } from "./http";

export const commsApi = {
  conversations: createResourceApi("/comms/conversations/")
  messages: createResourceApi("/comms/messages/"),
  attachments: createResourceApi("/comms/attachments/"),
  orderDiscussions: createResourceApi("/comms/order-discussions/"),
  notifications: createResourceApi("/comms/notifications/"),
  preferences: createResourceApi("/comms/notification-preferences/"),
  disputes: createResourceApi("/comms/disputes/"),
  searchIndex: createResourceApi("/comms/search-index/"),
  searchEvents: createResourceApi("/comms/search-events/"),
  search: (q: string, entityType = "") =>
    apiRequest(`/comms/search-index/${buildQuery({ q, entity_type: entityType })}`),
  myPreferences: () => apiRequest("/comms/notification-preferences/me/"),
  conversationMessages: (id: string | number) =>
    apiRequest<Record<string, unknown>[]>(`/comms/conversations/${id}/messages/`),
  sendConversationMessage: (id: string | number, data: unknown) =>
    apiRequest(`/comms/conversations/${id}/messages/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
