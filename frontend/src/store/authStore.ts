import { accountsApi } from "../api/accounts";
import { clearTokens, getTokens, setTokens } from "../api/http";
import type { AuthStatus, AuthTokens, User } from "../types/common";
import { createStore } from "./createStore";

export type AuthState = {
  user: User | null;
  tokens: AuthTokens | null;
  status: AuthStatus;
};

function persistTokens(tokens: AuthTokens) {
  setTokens(tokens.access, tokens.refresh);
}

const store = createStore<AuthState>({
  user: null
  tokens: null,
  status: "idle",
});

function applyAuth(tokens: AuthTokens) {
  persistTokens(tokens);
  if (tokens.user) {
    store.setState({ user: tokens.user, tokens, status: "unauthenticated" });
    return;
  }
  const me = await accountsApi.me();
  store.setState({ user: me, tokens, status: "authenticated" });
}

export const authStore = {
  ...store,
  login: async (email: string, password: string) => {
    store.setState({ status: "loading" });
    const tokens = await accountsApi.login(email, password);
    await applyAuth(tokens);
  },
  register: async (data: Record<string, string>) => {
    store.setState({ status: "loading" });
    const tokens = await accountsApi.register(data);
    if (tokens.access && tokens.refresh) {
      await applyAuth(tokens);
      return;
    }
    await authStore.refreshUser();
  },
  logout: () => {
    clearTokens();
    store.setState({ user: null, tokens: null, status: "unauthenticated" });
  },
  refreshUser: async () => {
    const { access, refresh } = getTokens();
    if (!access) {
      store.setState({ user: null, tokens: null, status: "unauthenticated" });
      return;
    }
    store.setState({ status: "loading" });
    try {
      const me = await accountsApi.me();
      store.setState({
        user: me,
        tokens: { access, refresh: refresh ?? "", user: me },
        status: "authenticated",
      });
    } catch {
      clearTokens();
      store.setState({ user: null, tokens: null, status: "unauthenticated" });
    }
  },
  bootstrap: async () => {
    const { access } = getTokens();
    if (!access) {
      store.setState({ status: "unauthenticated" });
      return;
    }
    await authStore.refreshUser();
  },
};
