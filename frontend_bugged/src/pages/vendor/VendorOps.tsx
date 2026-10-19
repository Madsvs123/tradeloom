import  useEffect, useState } from "react";
import Grid from "@mui/materail/Grid";
import Stack from "@mui/material/Stack";
import { vendorApi } from "../../api/vendor";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { StatCard } from "../../components/ui/StatCard";
import { Tabs } from "../../components/ui/Tabs";
import { useCollection } from "../../hooks/useCollection";
import { asCount, asRows } from "../../utils/format";

export default function VendorOps() {
  const [tab, setTab] = useState("orders");
  const orders = useCollection("/vendor/orders/");
  const inventory = useCollection("/vendor/inventory/items/");
  const payouts = useCollection("/vendor/payouts/");
  const [incoming, setIncoming] = useState<Record<string, unknown>>({});

  useEffect(() => {
    vendorApi.incomingWork().then((data) => setIncoming((data as Record<string, unknown>) ?? {})).catch(() => undefined);
  }, []);

  return (
    <Stack spacing={3}>
      <PageHeader title="Vendor operations" subtitle="Incoming work, inventory, price book, payouts, and disputes." />
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Incoming" value={asCount(incoming) || orders.count} detail="Open supplier work" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Inventory SKUs" value={inventory.count} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Payouts" value={payouts.count} />
        </Grid>
      </Grid>
      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: "orders", label: "Incoming orders" },
          { id: "inventory", label: "Inventory" },
          { id: "payouts", label: "Payouts" },
        ]}
      />
      <Card>
        {tab === "orders" ? (
          <DataTable
            loading={orders.loading}
            rows={orders.rows.length ? orders.rows : asRows(incoming)}
            columns={[
              { key: "id", label: "ID" },
              { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            ]}
          />
        ) : null}
        {tab === "inventory" ? (
          <DataTable
            loading={inventory.loading}
            rows={inventory.rows}
            columns={[
              { key: "sku", label: "SKU" },
              { key: "quantity_on_hand", label: "On hand" },
            ]}
          />
        ) : null}
        {tab === "payouts" ? (
          <DataTable
            loading={payouts.loading}
            rows={payouts.rows}
            columns={[
              { key: "id", label: "ID" },
              { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            ]}
          />
        ) : null}
      </Card>
    </Stack>
  );
}
