import { FormEvent, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import CardActionArea from "@mui/material/CardActionArea";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { createResourceApi } from "../../api/http";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { Input } from "../../components/ui/Input";
import { Modal } from "../../components/ui/Modal";
import { StatCard } from "../../components/ui/StatCard";
import { useCollection } from "../../hooks/useCollection";
import { useToast } from "../../hooks/useToast";
import type { ResourceDef } from "../../types/common";

export function ResourceWorkspace({ resource }: { resource: ResourceDef }) {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});
  const api = useMemo(() => createResourceApi(resource.path), [resource.path]);
  const { rows, count, loading, reload } = useCollection(resource.path, query ? { search: query } : undefined);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    try {
      const payload: Record<string, unknown> = {};
      resource.createFields.forEach((field) => {
        if (form[field] !== undefined && form[field] !== "") payload[field] = form[field];
      });
      await api.create(payload);
      toast(`${resource.label} created`, "success");
      setOpen(false);
      setForm({});
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Create failed", "error");
    }
  }

  return 
    <Stack spacing={3}>
      <PageHeader
        title={resource.label}
        subtitle={`Live ${resource.module} records from ${resource.path}`}
        actions={
          resource.createFields.length ? (
            <Button onClick={() => setOpen(true)}>New {resource.label.slice(0, -1)}</Button>
          ) : undefined
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <StatCard label="Records" value={count} />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard label="Loaded" value={rows.length} />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard label="Module" value={resource.module} />
        </Grid>
      </Grid>
      <Card>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 2 }}>
          <Input
            label={`Search ${resource.label.toLowerCase()}`}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <Button variant="secondary" onClick={() => void reload()}>
            Refresh
          </Button>
        </Stack>
        <DataTable
          loading={loading}
          rows={rows}
          emptyMessage={`No ${resource.label.toLowerCase()} yet`}
          onRowClick={(row) => navigate(`/workspace/${resource.module}/${resource.key}/${row.id || row.slug}`)}
          columns={resource.columns.map((key) => ({
            key,
            label: key.replace(/_/g, " "),
            render: (value) =>
              key.includes("status") || key.includes("published") ? <StatusChip value={value} /> : String(value ?? "—"),
          }))}
        />
      </Card>
      <Modal open={open} onClose={() => setOpen(false)} title={`Create ${resource.label}`}>
        <Stack component="form" spacing={2} onSubmit={onCreate} sx={{ pt: 1 }}>
          {resource.createFields.map((field) => (
            <Input
              key={field}
              label={field.replace(/_/g, " ")}
              value={form[field] ?? ""}
              onChange={(event) => setForm((current) => ({ ...current, [field]: event.target.value }))}
            />
          ))}
          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save</Button>
          </Stack>
        </Stack>
      </Modal>
    </Stack>
  );
}

export function ResourceHub({
  title,
  subtitle,
  items,
}: {
  title: string;
  subtitle: string;
  items: ResourceDef[];
}) {
  const navigate = useNavigate();
  return (
    <Stack spacing={2} sx={{ mt: 1 }}>
      <PageHeader title={title} subtitle={subtitle} />
      <Grid container spacing={2}>
        {items.map((item) => (
          <Grid item xs={12} sm={6} md={4} key={item.key}>
            <Card>
              <CardActionArea onClick={() => navigate(`/workspace/${item.module}/${item.key}`)} sx={{ p: 0.5 }}>
                <Typography variant="h3">{item.label}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {item.path}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {item.actions?.map((action) => action.label).join(" · ") || "List, create, inspect"}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
