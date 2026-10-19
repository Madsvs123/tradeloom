import { apiRequest, createResourceApi  from "./http";

export const workflowsApi = {
  definitions: createResourceApi("/workflows/definitions/"),
  instances: createResourceApi("/workflows/instances/"),
  tasks: createResourceApi("/workflows/tasks/"),
  transitions: createResourceApi("/workflows/transitions/"),
  escalationRules: createResourceApi("/workflows/escalation-rules/"),
  inbox: (data?: unknown) =>
    apiRequest("/workflows/inbox/", {
      method: data ? "POST" : "GET",
      body: data ? JSON.stringify(data) : undefined,
    }),
};
