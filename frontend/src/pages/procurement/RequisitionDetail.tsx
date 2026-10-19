import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { procurementApi } from "../../api/procurement";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useToast } from "../../hooks/useToast";
import { asRows, formatStatus } from "../../utils/format";

export default function RequisitionDetail() {
  const { id = "" } = useParams();
  const { toast } = useToast();
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [lines, setLines] = useState<Record<string, unknown>[]>([]);

  async function load() {
    const data = await procurementApi.requisitions.get(id);
    setRecord(data);
    const lineData = await procurementApi.requisitionLines.list({ requisition_id: id });
    setLines(asRows(lineData));
  }

  useEffect(() => {
    load().catch(() => toast("Unable to load requisition", "error"));
  }, [id, toast]);

  async function run(name: string, payload: Record<string, unknown> = {}) {
    try {
      const updated = await procurementApi.requisitions.action(id, name, payload);
      setRecord(updated);
      toast(`${name.replace(/-/g, " ")} completed, "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed", "error");
    }
  }

  if (!record) return null;

  return (
    <Stack spacing={3}>
      <PageHeader
        title={String(record.requisition_number ?? record.title ?? `Requisition ${id}`)}
        subtitle={formatStatus(record.status)}
        actions={
          <>
            <Button variant="secondary" onClick={() => void run("submit")}>
              Submit
            </Button>
            <Button onClick={() => void run("convert-to-rfq", { notes: "Converted from requisition" })}>
              Convert to RFQ
            </Button>
          </>
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card title="Header">
            <Stack spacing={2}>
              <Typography{String(record.description ?? "")}</Typography>
              <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                <Typography variant="body2">Dept {String(record.department_code ?? "—")}</Typography>
                <Typography variant="body2">Category {String(record.category ?? "—")}</Typography>
              </Stack>
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card title="Lines">
            <Stack spacing={2}>
              {lines.map((line) => (
                <Stack
                  key={String(line.id)}
                  direction="row"
                  spacing={2}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Typography fontWeight={700}>{String(line.description ?? line.id)}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    qty {String(line.quantity ?? 1)}
                  </Typography>
                </Stack>
              ))}
              {!lines.length ? <Typography color="text.secondary">No line items yet.</Typography> : null}
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
