import { useCallback, useEffect, useState } from "react";
import { createResourceApi } from "../api/http";
import type { QueryParams } from "../types/common";
import { asCount, asRows } from "../utils/format";
import { useToast } from "./useToast";

export function useCollection(path: string, params?: QueryParams) {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const paramKey = params ? JSON.stringify(params) : "";

  const load = useCallback(() => {
    if (!path) {
      setRows([]);
      setCount(0);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const api = createResourceApi(path);
      const data = await api.list(params);
      const results = asRows(data);
      setRows(results);
      setCount(asCount(data, results));
    } catch (err) {
      setRows([]);
      setCount(0);
      const message = err instanceof Error ? err.message : "Unable to load records";
      setError(message);
      toast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [path, paramKey, toast]);

  useEffect(() => {
    load();
  }, [load]);

  return { rows, count, loading, error, reload: load, setRows };
}
