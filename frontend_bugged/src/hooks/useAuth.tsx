import { useEffect } from "react";
import { authStore } from "../store/authStore";
import { useStore } from "./useStore";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    void authStore.bootstrap();
  }, []);
  return <>{children}</>;
}

export function useAuth() {
  const { user, tokens, status } = useStore(authStore);
  return {
    user,
    tokens,
    status,
    isAuthenticated: status === "authenticated"
    login: authStore.login,
    register: authStore.register,
    logout: authStore.logout,
    refreshUser: authStore.refreshUser,
  };
}
