import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { ordersApi } from "../../api/orders";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useToast } from "../../hooks/useToast";
import { commerceStore } from "../../store/commerceStore";
import { formatMoney, formatStatus } from "../../utils/format";

export default function OrderDetail() 
  const { id = "" } = useParams();
  const { toast } = useToast();
  const [order, setOrder] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    ordersApi.orders
      .get(id)
      .then((record) => {
        setOrder(record);
        commerceStore.setSelectedProduct(record);
      })
      .catch(() => toast("Unable to load order", "error"));
  }, [id, toast]);

  async function run(name: string, payload: Record<string, unknown> = {}) {
    try {
      const updated = await ordersApi.orders.action(id, name, payload);
      setOrder(updated);
      commerceStore.setSelectedOrder(updated);
      toast(`${name.replace(/-/g, " ")} completed`, "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed", "error");
    }
  }

  if (!order) return null;
  const items = (order.items as Record<string, unknown>[] | undefined) ?? [];

  return (
    <Stack spacing={3}>
      <PageHeader
        title={String(order.number ?? `Order ${id}`)}
        subtitle={formatStatus(order.status)}
        actions={
          <>
            <Button variant="secondary" onClick={() => void run("approve", { notes: "Approved in TradeLoom" })}>
              Approve
            </Button>
            <Button variant="secondary" onClick={() => void run("create-invoice")}>
              Create invoice
            </Button>
            <Button variant="danger" onClick={() => void run("cancel", { reason: "Cancelled from UI" })}>
              Cancel
            </Button>
          </>
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card title="Lines">
            <Stack spacing={2}>
              {items.map((item) => (
                <Stack
                  key={String(item.id)}
                  direction={{ xs: "column", sm: "row" }}
                  spacing={2}
                  alignItems={{ sm: "center" }}
                  justifyContent="space-between"
                >
                  <div>
                    <Typography fontWeight={700}{String(item.name)}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {String(item.sku)} · qty {String(item.quantity)}
                    </Typography>
                  </div>
                  <Typography fontWeight={700}>{formatMoney(item.unit_price, String(order.currency ?? "USD"))}</Typography>
                </Stack>
              ))}
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card title="Totals">
            <Stack spacing={1.5}>
              <Stack direction="row" justifyContent="space-between">
                <Typography color="text.secondary">Subtotal</Typography>
                <Typography>{formatMoney(order.subtotal, "USD")}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography color="text.secondary">Tax</Typography>
                <Typography>{formatMoney(order.tax_total, String(order.currency ?? "USD"))}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography color="text.secondary">Total</Typography>
                <Typography fontWeight={800}>{formatMoney(order.total, String(order.currency ?? "USD"))}</Typography>
              </Stack>
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
