import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { logisticsApi } from "../../api/logistics";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { StatusChip } from "../../components/ui/DataTable";
import { useToast } from "../../hooks/useToast";
import { asRows, formatStatus } from "../../utils/format";

export default function ShipmentPlanDetail() {
  const { id = "" } = useParams();
  const { toast } = useToast();
  const [plan, setPlan] = useState<Record<string, unknown> | null>(null);
  const [events, setEvents] = useState<Record<string, unknown>[]>([]);

  async function load() {
    const record = await logisticsApi.shipmentPlans.get(id);
    setPlan(record);
    const tracking = await logisticsApi.trackingEvents.list({ shipment_plan: id });
    setEvents(asRows(tracking));
  }

  useEffect(() => {
    load().catch(() => toast("Unable to load shipment plan", "error"));
  }, [id, toast]);

  async function packingList() {
    try {
      await logisticsApi.shipmentPlans.action(id, "packing-list", {
        packing_list_number: `PL-${id}`,
        remarks: "Created from logistics tower",
      });
      toast("Packing list created", "success");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to create packing list", "error");
    }
  }

  if (!plan) return null;

  return (
    <Stack spacing={3}>
      <PageHeader
        title={String(plan.plan_number || `Plan ${id}`)}
        subtitle={`${formatStatus(plan.status)} · ${String(plan.mode ?? "")}`}
        actions={<Button onClick={() => void packingList()}>Create packing list</Button>}
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card title="Destination">
            <Typography>
              {String(plan.destination_name ?? "")} · {String(plan.destination_country ?? "")}
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card title="Tracking">
            <Stack spacing={2}>
              {events.flatMap((event) => (
                <Stack
                  key={String(event.id)}
                  direction="row"
                  spacing={2}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <StatusChip value={event.status} />
                  <Typography variant="body2" color="text.secondary">
                    {String(event.occurred_at ?? "")}
                  </Typography>
                </Stack>
              ))}
              {!events.length ? <Typography color="text.secondary">No tracking events yet.</Typography> : null}
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
