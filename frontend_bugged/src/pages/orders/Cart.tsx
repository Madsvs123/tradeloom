import  useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { useStore } from "../../hooks/useStore";
import { useToast } from "../../hooks/useToast";
import { commerceStore } from "../../store/commerceStore";
import { formatMoney } from "../../utils/format";

export default function Cart() 
  const navigate = useNavigate();
  const { toast } = useToast();
  const cart = useStore(commerceStore, (state) => state.currentCart);
  const loading = useStore(commerceStore, (state) => state.cartLoading);
  const draft = useStore(commerceStore, (state) => state.checkoutDraft);

  useEffect(() => {
    void commerceStore.loadCart();
  }, []);

  const items = (cart?.items as Record<string, unknown>[] | undefined) ?? [];

  async function checkout() {
    try {
      const order = await commerceStore.checkout();
      toast("Order created from cart", "success");
      navigate(`/orders/${(order as { id?: string }).id ?? ""}`);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Checkout failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Cart"
        subtitle="Recalculate pricing, taxes, and convert the open cart into a purchase order."
        actions={
          <>
            <Button variant="secondary" onClick={() => void commerceStore.recalculate()}>
              Recalculate
            </Button>
            <Button onClick={() => void checkout()} disabled={loading || !items.length}>
              Checkout
            </Button>
          </>
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card title={`${items.length} line items`}>
            <Stack spacing={2}>
              {items.map((item) => (
                <Stack key={String(item.id)} direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }} justifyContent="space-between">
                  <div>
                    <Typography fontWeight={700}>{String(item.name)}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {String(item.sku)}
                    </Typography>
                  </div>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Input
                      type="number"
                      label="Qty"
                      sx={{ width: 96 }}
                      value={String(item.quantity ?? 1)}
                      onChange={(event) => void commerceStore.updateCartItem(String(item.id), Number(event.target.value))}
                    />
                    <Typography>{formatMoney(item.unit_price, String(item.currency ?? "USD"))}</Typography>
                    <Button size="sm" variant="ghost" onClick={() => void commerceStore.removeCartItem(String(item.id))}>
                      Remove
                    </Button>
                  </Stack>
                </Stack>
              ))}
              {!items.length ? <Typography color="text.secondary">Cart is empty. Add products from the marketplace.</Typography> : null}
              {cart ? (
                <Stack direction="row" justifyContent="space-between">
                  <Typography>Subtotal {formatMoney(cart.subtotal, String(cart.currency ?? "USD"))}</Typography>
                  <Typography fontWeight={800}>Total {formatMoney(cart.total, String(cart.currency ?? "USD"))}</Typography>
                </Stack>
              ) : null}
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card title="Checkout draft">
            <Stack spacing={2}>
              <Textarea label="Notes" value={draft.notes} onChange={(event) => commerceStore.setCheckoutDraft({ notes: event.target.value })} />
              <Input
                label="Need-by date"
                type="date"
                value={draft.requested_delivery_date}
                onChange={(event) => commerceStore.setCheckoutDraft({ requested_delivery_date: event.target.value })}
                InputLabelProps={{ shrink: true }}
              />
              <Input
                label="Payment terms"
                value={draft.payment_terms}
                onChange={(event) => commerceStore.setCheckoutDraft({ payment_terms: event.target.value })}
              />
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
