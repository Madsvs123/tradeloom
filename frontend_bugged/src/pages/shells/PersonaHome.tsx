import { useEffect } from "react";
import { Link as RouterLink } from "react-router";
import CardActionArea from "@mui/materail/CardActionArea";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { sessionStore } from "../../store/sessionStore";
import type { Persona } from "../../types/common";

const SHELLS = {
  buy: {
    title: "Buyer workspace",
    subtitle: "Requisitions, catalog, RFQs, contracts, orders, and approvals.",
    links: [
      ["/procurement", "Requisitions"],
      ["/marketplace", "Catalog"],
      ["/rfqs", "RFQs"],
      ["/contracts", "Contracts"],
      ["/cart", "Cart"],
      ["/orders", "Orders"],
      ["/inbox", "Approvals"],
      ["/finance", "Settlements"],
    ],
  },
  sell: {
    title: "Supplier workspace",
    subtitle: "Storefront, quote desk, incoming work, inventory, and payouts.",
    links: [
      ["/marketplace", "Storefront"],
      ["/rfqs", "Quote desk"],
      ["/vendor", "Incoming work"],
      ["/vendor", "Payouts"],
      ["/logistics", "Fulfillment"],
      ["/contracts", "Agreements"],
      ["/messages", "Threads"],
    ],
  },
  ops: {
    title: "Operator workspace",
    subtitle: "Trust, workflows, analytics, integrations, and platform controls.",
    links: [
      ["/compliance", "Trust"],
      ["/inbox", "Workflow inbox"],
      ["/analytics", "Analytics"],
      ["/integrations", "Integrations"],
      ["/platform", "Platform admin"],
      ["/finance", "Finance ops"],
      ["/settings", "Accounts"],
    ],
  },
} as const;

export default function PersonaHome({ persona }: { persona: Persona }) {
  const shell = SHELLS[persona];

  useEffect(() => {
    sessionStore.setPersona(persona);
  }, [persona]);

  return (
    <Stack spacing={3}>
      <PageHeader title={shell.title} subtitle={shell.subtitle} />
      <Grid container spacing={2}>
        {shell.links.map(([path, label]) => (
          <Grid item xs={12} sm={6} md={4} key={path + label}>
            <Card>
              <CardActionArea component={RouterLink} to={path} sx={{ p: 0.5 }}>
                <Typography variant="h3">{label}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {path}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Card title="Cross-cutting">
        <Typography color="text.secondary">
          Approvals, search, and notifications sit on every record via inbox and the command palette (Ctrl/Cmd+K).
        </Typography>
      </Card>
    </Stack>
  );
}
