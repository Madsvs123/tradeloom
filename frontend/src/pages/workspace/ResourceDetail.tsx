import  FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { createResourceApi } from "../../api/http";
import { resourceByKey } from "../../catalog";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Modal } from "../../components/ui/Modal";
import { PageSpinner } from "../../components/ui/Spinner";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/format";

export default function ResourceDetail() 
  const { resourceKey = "", id = "" } = useParams();
  const resource = resourceByKey(resourceKey);
  const navigate = useNavigate();
  const { toast } = useToast();
  const api = useMemo(() => (resource ? createResourceApi(resource.path) : null), [resource]);
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [actionName, setActionName] = useState<string | null>(null);
  const [fields, setFields] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!api) return;
    api
      .get(id)
      .then(setRecord)
      .catch(() => toast("Unable to load record", "error"));
  }, [api, id, toast]);

  if (!resource || !api) return <Typography color="text.secondary">Unknown resource.</Typography>;
  if (!record) return <PageSpinner />;

  async function runAction(event: FormEvent) {
    event.preventDefault();
    if (!actionName || !resource || !api) return;
    const spec = resource.actions?.find((item) => item.name === actionName);
    try {
      const payload: Record<string, unknown> = {};
      (spec?.fields ?? []).forEach((field) => {
        if (fields[field]) payload[field] = fields[field];
      });
      const result = spec?.collection
        ? await api.collectionPost(actionName, payload)
        : spec?.method === "GET"
          ? await api.collectionGet(actionName)
          : await api.action(id, actionName, payload);
      if (result && typeof result === "object") setRecord(result as Record<string, unknown>);
      toast(`${spec?.label ?? actionName} completed`, "success");
      setActionName(null);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title={String(record.name ?? record.title ?? record.reference ?? record.number ?? resource.label)}
        subtitle={`${resource.path}${id}/`}
        actions={
          <Button variant="secondary" onClick={() => navigate(-1)}>
            Back
          </Button>
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card title="Record">
            <Stack spacing={1.5}>
              {Object.entries(record)
                .filter(([, value]) => value !== null && typeof value !== "object")
                .slice(0, 24)
                .map(([key, value]) => (
                  <Stack key={key} direction="row" justifyContent="space-between" spacing={2}>
                    <Typography color="text.secondary">{key.replace(/_/g, " ")}</Typography>
                    <Typography>{key.endsWith("_at") ? formatDateTime(value) : String(value)}</Typography>
                  </Stack>
                ))}
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card title="Workflow actions">
            <Stack spacing={1}>
              {(resource.actions ?? []).map((action) => (
                <Button key={action.name} variant="secondary" onClick={() => setActionName(action.name)}>
                  {action.label}
                </Button>
              ))}
              {!resource.actions?.length ? (
                <Typography color="text.secondary">
                  Use PATCH from the API client or return to the list to create related records.
                </Typography>
              ) : null}
            </Stack>
          </Card>
        </Grid>
      </Grid>
      <Modal open={Boolean(actionName)} onClose={() => setActionName(null)} title={actionName ?? ""}>
        <Stack component="div" spacing={2} onSubmit={runAction} sx={{ pt: 1 }}>
          {(resource.actions?.find((item) => item.name === actionName)?.fields ?? []).map((field) => (
            <Input
              key={field}
              label={field.replace(/_/g, " ")}
              value={fields[field] ?? ""}
              onChange={(event) => setFields((current) => ({ ...current, [field]: event.target.value }))}
            />
          ))}
          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button type="button" variant="ghost" onClick={() => setActionName(null)}>
              Cancel
            </Button>
            <Button type="submit">Run</Button>
          </Stack>
        </Stack>
      </Modal>
    </Stack>
  );
}
