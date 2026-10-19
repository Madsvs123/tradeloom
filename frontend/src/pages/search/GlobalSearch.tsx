import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { commsApi } from "../../api/comms";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { asRows } from "../../utils/format";

export default function GlobalSearch() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get("q") ?? "");
  const [entityType, setEntityType] = useState("");
  const [results, setResults] = useState<Record<string, unknown>[]>([]);

  async function run(event?: FormEvent) {
    event?.preventDefault();
    setParams({ q: query });
    const data = await commsApi.search(query, entityType);
    setResults(asRows(data));
  }

  useEffect(() => {
    if (query) void run();
  }, []);

  return (
    <Stack spacing={3}>
      <PageHeader title="Global search" subtitle="Indexed products, suppliers, RFQs, orders, invoices, and conversations." />
      <Card>
        <Stack spacing={2}>
          <Stack component="form" direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }} onSubmit={run}>
            <Input
              label="Search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search the commercial graph"
            />
            <Select label="Type" value={entityType} onChange={(event) => setEntityType(event.target.value)}>
              <MenuItem value="">All types</MenuItem>
              <MenuItem value="product">Products</MenuItem>
              <MenuItem value="supplier">Suppliers</MenuItem>
              <MenuItem value="rfq">RFQs</MenuItem>
              <MenuItem value="order">Orders</MenuItem>
              <MenuItem value="invoice">Invoices</MenuItem>
            </Select>
            <Button type="submit">Search</Button>
          </Stack>
          {results.flatMap((item) => (
            <Stack key={String(item.id)} spacing={0.5}>
              <Typography fontWeight={700}>{String(item.title ?? item.name ?? item.id)}</Typography>
              <Typography variant="body2" color="text.secondary">
                {String(item.entity_type ?? "")} · {String(item.description ?? "")}
              </Typography>
            </Stack>
          ))}
          {!results.length ? <Typography color="text.secondary">No indexed matches.</Typography> : null}
        </Stack>
      </Card>
    </Stack>
  );
}
