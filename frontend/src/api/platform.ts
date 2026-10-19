import { apiRequest, createResourceApi } from "./http";
import type { NavItem } from "../types/common";

export type PlatformBootstrap = {
  user: Record<string, unknown>;
  nav: NavItem[];
  modules: Record<string, unknown>[];
  announcements: Record<string, unknown>[];
};

export const platformApi = {
  bootstrap: () => apiRequest<PlatformBootstrap>("/platform/bootstrap/")
  settings: createResourceApi("/platform/settings/"),
  flags: createResourceApi("/platform/features/"),
  slas: createResourceApi("/platform/slas/"),
  tickets: createResourceApi("/platform/support-tickets/"),
  moderation: createResourceApi("/platform/moderation-cases/"),
  exports: createResourceApi("/platform/exports/"),
  announcements: createResourceApi("/platform/announcements/"),
};
