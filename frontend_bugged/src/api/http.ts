import type { Paginated, QueryParams } from "../types/common";

export const API_BASE = "/api";
export const ACCESS_KEY = "access_token";
export const REFRESH_KEY = "tradeloom_refresh";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function buildQuery(params?: QueryParams): string 
  if (!params) return "";
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value = undefined || value === null || value === "") return;
    search.set(key, String(value));
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function getTokens() {
  if (typeof localStorage === "undefined") return { access: null, refresh: null };
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  };
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const { refresh } = getTokens();
    if (!refresh) return null;
    const res = await fetch(`${API_BASE}/accounts/auth/token/refresh/, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) {
      clearTokens();
      return null;
    }
    const data = (await res.json()) as { access?: string; refresh?: string };
    if (!data.access) {
      clearTokens();
      return null;
    }
    localStorage.setItem(ACCESS_KEY, data.access);
    if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh);
    return data.access;
  })();
  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

function extractErrorMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;
  const record = data as Record<string, unknown>;
  if (typeof record.detail === "string") return record.detail;
  if (Array.isArray(record.non_field_errors) && typeof record.non_field_errors[0] === "string") {
    return record.non_field_errors[0];
  }
  const first = Object.values(record).find((value) => Array.isArray(value) && typeof value[0] === "string");
  if (Array.isArray(first) && typeof first[0] === "string") return first[0];
  return fallback;
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let { access } = getTokens();
  if (access) headers.set("Authorization", `Bearer ${access}`);

  const execute = () => fetch(`${API_BASE}${path}`, { ...options, headers });
  let response = await execute();

  if (response.status === 401 && getTokens().refresh) {
    access = await refreshAccessToken();
    if (access) {
      headers.set("Authorization", `Bearer ${access}`);
      response = await execute();
    }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(extractErrorMessage(data, "Request failed"), response.status, data);
  }
  if (response.status === 204) return undefined as T;
  const text = await response.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

export type ResourceApi = {
  list: (params?: QueryParams) => Promise<Paginated>;
  get: (id: string | number) => Promise<Record<string, unknown>>;
  create: (data: unknown) => Promise<Record<string, unknown>>;
  update: (id: string | number, data: unknown) => Promise<Record<string, unknown>>;
  remove: (id: string | number) => Promise<unknown>;
  action: (id: string | number, name: string, data?: unknown) => Promise<Record<string, unknown>>;
  collectionGet: (name: string, params?: QueryParams) => Promise<unknown>;
  collectionPost: (name: string, data?: unknown) => Promise<unknown>;
};

export function createResourceApi(base: string): ResourceApi {
  const root = base.endsWith("/") ? base : `${base}/`;
  return {
    list: (params) => apiRequest<Paginated>(`${root}${buildQuery(params)}`),
    get: (id) => apiRequest<Record<string, unknown>>(`${root}${id}/`),
    create: (data) => apiRequest<Record<string, unknown>>(root, { method: "POST", body: JSON.stringify(data) }),
    update: (id, data) =>
      apiRequest<Record<string, unknown>>(`${root}${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
    remove: (id) => apiRequest(`${root}${id}/`, { method: "DELETE" }),
    action: (id, name, data) =>
      apiRequest<Record<string, unknown>>(`${root}${id}/${name}/`, {
        method: "POST",
        body: data === undefined ? undefined : JSON.stringify(data),
      }),
    collectionGet: (name, params) => apiRequest(`${root}${name}/${buildQuery(params)}`),
    collectionPost: (name, data) =>
      apiRequest(`${root}${name}/`, {
        method: "POST",
        body: data === undefined ? undefined : JSON.stringify(data),
      }),
  };
}
