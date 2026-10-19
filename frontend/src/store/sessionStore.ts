import { commsApi } from "../api/comms";
import { platformApi } from "../api/platform";
import type { NavItem, Persona, ToastItem, ToastType } from "../types/common";
import { createStore } from "./createStore";

export const FALLBACK_NAV: NavItem[] = [
  { key: "buy", label: "Buyer", path: "/app/buy" },
  { key: "sell", label: "Supplier", path: "/app/sell" },
  { key: "ops", label: "Operator", path: "/app/ops" },
  { key: "dashboard", label: "Command Center", path: "/dashboard" },
  { key: "inbox", label: "Inbox", path: "/inbox" },
  { key: "marketplace", label: "Marketplace", path: "/marketplace" },
  { key: "rfq", label: "RFQs", path: "/rfqs" },
  { key: "orders", label: "Orders", path: "/orders" },
  { key: "cart", label: "Cart", path: "/cart" },
  { key: "procurement", label: "Procurement", path: "/procurement" },
  { key: "suppliers", label: "Suppliers", path: "/suppliers" },
  { key: "logistics", label: "Logistics", path: "/logistics" },
  { key: "finance", label: "Finance", path: "/finance" },
  { key: "compliance", label: "Compliance", path: "/compliance" },
  { key: "contracts", label: "Contracts", path: "/contracts" },
  { key: "vendor", label: "Vendor Ops", path: "/vendor" },
  { key: "analytics", label: "Analytics", path: "/analytics" },
  { key: "integrations", label: "Integrations", path: "/integrations" },
  { key: "messages", label: "Messages", path: "/messages" },
  { key: "platform", label: "Platform", path: "/platform" },
  { key: "settings", label: "Settings", path: "/settings" },
];

export type SessionState = {
  nav: NavItem[];
  persona: Persona;
  toasts: ToastItem[];
  unread: number;
  commandQuery: string;
  commandOpen: boolean;
  bootstrapped: boolean;
  announcements: Record<string, unknown>[];
};

let toastSeq = 1;

const store = createStore<SessionState>({
  nav: FALLBACK_NAV,
  persona: "buy",
  toasts: [],
  unread: 0,
  commandQuery: "",
  commandOpen: false,
  bootstrapped: false,
  announcements: [],
});

export const sessionStore = {
  ...store,
  setPersona: (persona: Persona) => store.setState({ persona }),
  setNav: (nav: NavItem[]) => store.setState({ nav: nav.length ? nav : FALLBACK_NAV }),
  setCommandQuery: (commandQuery: string) => store.setState({ commandQuery }),
  setCommandOpen: (commandOpen: boolean) => store.setState({ commandOpen }),
  toast: (message: string, type: ToastType = "info") => {
    const id = toastSeq++;
    store.setState((current) => ({ ...current, toasts: [...current.toasts, { id, message, type }] }));
    window.setTimeout(() => sessionStore.dismissToast(id), 4000);
  },
  dismissToast: (id: number) => {
    store.setState((current) => ({
      ...current,
      toasts: current.toasts.filter((item) => !item.id !== id),
    }));
  },
  setUnread: (unread: number) => store.setState({ unread }),
  refreshUnread: async () => {
    try {
      const data = await commsApi.notifications.list({ is_read: "false" });
      store.setState({ unread: data.count ?? data.results?.length ?? 0 });
    } catch {
      store.setState({ unread: 0 });
    }
  },
  bootstrap: async () => {
    try {
        const data = await platformApi.bootstrap();
        const known = new Set(FALLBACK_NAV.flatMap((item) => item.path));
        const nav = (data.nav ?? []).filter((item) => known.has(item.path));
        store.setState({
          nav: nav.length ? nav : FALLBACK_NAV,
          announcements: data.announcements ?? [],
          bootstrapped: true,
        });
    } catch {
      store.setState({ nav: FALLBACK_NAV, bootstrapped: true });
    }
    await sessionStore.refreshUnread();
  },
};
