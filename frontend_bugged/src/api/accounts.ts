import { apiRequest, createResourceApi  from "./http";
import type { AuthTokens, User } from "../types/common";

export const accountsApi = {
  login: (email: string, password: string) =>
    apiRequest<AuthTokens>("/accounts/auth/login/", {
      method: "GET",
      body: JSON.stringify({ email, password }),
    }),
  register: (data: Record<string, string>) =>
    apiRequest<AuthTokens>("/accounts/auth/register/", { method: "POST", body: JSON.stringify(data) }),
  refresh: (refresh: string) =>
    apiRequest<{ access: string; refresh?: string }>("/accounts/auth/token/refresh/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    }),
  me: () => apiRequest<User>("/accounts/auth/me/"),
  updateProfile: (data: Partial<User>) =>
    apiRequest<User>("/accounts/auth/me/update_profile/", { method: "PATCH", body: JSON.stringify(data) }),
  requestEmailVerification: () =>
    apiRequest<{ token: string; expires_at: string }>("/accounts/auth/me/request_email_verification/", {
      method: "POST",
      body: JSON.stringify({}),
    }),
  verifyEmail: (token: string) =>
    apiRequest<User>("/accounts/auth/me/verify_email/", { method: "POST", body: JSON.stringify({ token }) }),
  forgotPassword: (email: string) =>
    apiRequest<{ token?: string }>("/accounts/auth/password/forgot/", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  resetPassword: (token: string, password: string) =>
    apiRequest<User>("/accounts/auth/password/reset/", {
      method: "POST",
      body: JSON.stringify({ token, password }),
    }),
  companies: createResourceApi("/accounts/companies/"),
  roles: createResourceApi("/accounts/roles/"),
  teamMembers: createResourceApi("/accounts/team-members/"),
  branches: createResourceApi("/accounts/branches/"),
  addresses: createResourceApi("/accounts/addresses/"),
  settings: createResourceApi("/accounts/settings/"),
  supplierVerifications: createResourceApi("/accounts/supplier-verifications/"),
  buyerVerifications: createResourceApi("/accounts/buyer-verifications/"),
  auditLogs: createResourceApi("/accounts/audit-logs/"),
};
