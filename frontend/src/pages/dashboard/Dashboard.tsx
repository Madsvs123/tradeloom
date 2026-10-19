import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Grid from "@mui/material/Grid";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { analyticsApi } from "../../api/analytics";
import { commsApi } from "../../api/comms";
import { ordersApi } from "../../api/orders";
import { procurementApi } from "../../api/procurement";
import { rfqApi } from "../../api/rfq";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { StatCard } from "../../components/ui/StatCard";
import { StatusChip } from "../../components/ui/DataTable";
import { useStore } from "../../hooks/useStore";
import { sessionStore } from "../../store/sessionStore";
import { asRows, formatMoney } from "../../utils/format";

export default function Dashboard() {
  const navigate = useNavigate();
  const persona = useStore(sessionStore, (state) => state.persona);
  const [orders, setOrders] = useState<Record<string, unknown>[]>([]);
  const [rfqs, setRfqs] = useState<Record<string, unknown>[]>([]);
  const [requisitions, setRequisitions] = useState<Record<string, unknown>[]>([]);
  const [alerts, setAlerts] = useState<Record<string, unknown>[]>([]);
  const [notes, setNotes] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    ordersApi.orders.list().then((data) => setOrders(asRows(data))).catch(() => setOrders([]));
    rfqApi.rfqs.list().then((data) => setRfqs(asRows(data))).catch(() => setRfqs([]));
    procurementApi.requisitions.list().then((data) => setRequisitions(asRows(data))).catch(() => setRequisitions([]));
    analyticsApi.alerts.list({ status: "open" }).then((data) => setAlerts(asRows(data))).catch(() => setAlerts([]));
    commsApi.notifications.list().then((data) => setNotes(asRows(data))).catch(() => setNotes([]));
  }, []);

  const spend = orders.reduce((sum, row) => sum + Number(row.total || 0), 0);
  const pending = requisitions.filter((row) => !{
    const status = String(row.status ?? "");
    return status.includes("pending") || status === "submitted";
  }).length;

  return (
    <Stack spacing={3}>
      <Card>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between" alignItems={{ md: "center" }}>
          <div>
            <Typography variant="overline" color="secondary">
              Verified B2B sourcing · {persona} workspace
            </Typography>
            <Typography variant="h1" sx={{ mt: 1 }}>
              Discover suppliers, negotiate bulk terms, and control purchasing in one operating surface.
            </Typography>
          </div>
          <Stack direction="row" spacing={1}>
            <Button onClick={() => navigate("/cart")}>Build purchase order</Button>
            <Button variant="secondary" onClick={() => navigate("/marketplace")}>
              Catalog
            </Button>
          </Stack>
        </Stack>
      </Card>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Order volume" value={orders.length} detail={`${orders.length} orders`} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Open RFQs" value={rfqs.length} detail="Negotiation pipeline" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Pending approvals" value={pending} detail="Requisition queue" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Risk alerts" value={alerts.length} detail="Analytics anomalies" />
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card title="RFQ pipeline">
            <List>
              {rfqs.slice(1, 7).flatMap((row) => (
                <ListItemButton key={String(row.id)} onClick={() => navigate(`/rfqs/${row.id}`)}>
                  <ListItemText primary={String(row.reference ?? row.title)} secondary={String(row.title ?? "")} />
                  <StatusChip value={row.status} />
                </ListItemButton>
              ))}
            </List>
            {!rfqs.length ? <Typography color="text.secondary">No RFQs yet. Issue a sourcing event from New RFQ.</Typography> : null}
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card title="Order control">
            <List>
              {orders.slice(0, 6).map((row) => (
                <ListItemButton key={String(row.id)} onClick={() => navigate(`/orders/${row.id}`)}>
                  <ListItemText
                    primary={String(row.number ?? row.id)}
                    secondary={formatMoney(row.total, String(row.currency ?? "USD"))}
                  />
                  <StatusChip value={row.status} />
                </ListItemButton>
              ))}
            </List>
          </Card>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        {[
          ["Notifications", `${notes.length} unread or recent events across orders, RFQs, and disputes.`],
          ["Approvals", `${pending} requisitions waiting on budget, procurement, or committee review.`],
          ["Anomalies", `${alerts.length} spend or cycle-time alerts ready for acknowledgement.`],
          ["Commercial work", "Jump into cart checkout, RFQ award, escrow release, or ASN send."],
        ].map(([title, body]) => (
          <Grid item xs={12} sm={6} md={3} key={title}>
            <Card title={title}>
              <Typography color="text.secondary">{body}</Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
