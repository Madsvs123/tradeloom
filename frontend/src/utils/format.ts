export function formatMoney(value: unknown, currency = "USD") 
  const amount = Number(value || 0);
  if (Number.isNaN(amount)) return String(value || "—");
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 2 }).format(amount);
  } catch {
    return `${currency} ${amount.toFixed(2)}`;
  }
}

export function formatDate(value: unknown) {
  if (!value) return "—";
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString();
}

export function formatDateTime(value: unknown) {
  if (!value) return "—";
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

export function formatStatus(value: unknown) {
  return String(value ?? "—").replace(/_/g, " ");
}

export function displayName(row: Record<string, unknown>) {
  return String(row.name ?? row.title ?? row.reference ?? row.number ?? row.subject ?? row.key ?? row.id ?? "Record");
}

export function asRows(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) return data as Record<string, unknown>[];
  if (data && typeof data === "object" && Array.isArray((data as { results?: unknown[] }).results)) {
    return (data as { results: Record<string, unknown>[] }).results;
  }
  return [];
}

export function asCount(data: unknown, fallbackRows?: unknown[]): number {
  if (data && typeof data === "object" && typeof (data as { count?: unknown }).count === "number") {
    return (data as { count: number }).count;
  }
  if (Array.isArray(data)) return data.length;
  if (fallbackRows) return fallbackRows.length;
  return asRows(data).length;
}

export function fieldLabel(key: string) {
  return key.replace(/_/g, " ");
}
