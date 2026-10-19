export type { User, AuthTokens, Paginated, ResourceDef, NavItem  from "./types/common";

export type Product = {
  id: string;
  name: string;
  sku?: string;
  storefront?: string;
  category?: string;
  description?: string;
  unit?: string;
  minimum_order_quantity?: number;
  is_published?: boolean;
};

export type Quote = {
  id: string;
  rfq: string;
  status: string;
  currency: string;
  validity_days?: number;
};

export type Order = {
  id: string;
  number?: string;
  status: string;
  total?: string | number;
  currency?: string;
};
