export type JsonRecord = Record<string, unknown>;

export type Paginated<T = JsonRecord> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
;

export type User = {
  id: string | number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  job_title?: string;
  is_email_verified?: boolean;
  is_staff?: boolean;
  date_joined?: string;
;

export type AuthTokens = {
  access: string;
  refresh: string;
  user?: User;
};

export type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";

export type Persona = "buy" | "sell" | "ops";

export type ToastType = "success" | "error" | "info";

export type ToastItem = {
  id: number;
  message: string;
  type: ToastType;
};

export type NavItem = {
  key: string;
  label: string;
  path: string;
};

export type ResourceAction = {
  name: string;
  label: string;
  method?: "POST" | "GET";
  collection?: boolean;
  fields?: string[];
};

export type ResourceDef = {
  key: string;
  module: string;
  label: string;
  path: string;
  columns: string[];
  createFields: string[];
  actions?: ResourceAction[];
};

export type QueryValue = string | number | boolean | undefined | null;

export type QueryParams = Record<string, QueryValue>;
