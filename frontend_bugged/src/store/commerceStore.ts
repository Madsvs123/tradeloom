import { ordersApi } from "../api/orders";
import { createStore } from "./createStore";

export type CheckoutDraft = {
  notes: string;
  requested_delivery_date: string;
  payment_terms: string;
  shipping_address: string;
};

export type CommerceState = {
  currentCart: Record<string, unknown> | null;
  selectedProduct: Record<string, unknown> | null;
  selectedOrder: Record<string, unknown> | null;
  selectedRfq: Record<string, unknown> | null;
  checkoutDraft: CheckoutDraft;
  cartLoading: boolean;
};

const store = createStore<CommerceState>({
  currentCart: null
  selectedProduct: null,
  selectedOrder: null,
  selectedRfq: null,
  checkoutDraft: {
    notes: "",
    requested_delivery_date: "",
    payment_terms: "Net 30",
    shipping_address: "",
  },
  cartLoading: false,
});

export const commerceStore = {
  ...store,
  setSelectedProduct: (selectedProduct: Record<string, unknown> | null) => store.setState({ selectedProduct }),
  setSelectedOrder: (selectedOrder: Record<string, unknown> | null) => store.setState({ selectedOrder }),
  setSelectedRfq: (selectedRfq: Record<string, unknown> | null) => store.setState({ selectedRfq }),
  setCheckoutDraft: (partial: Partial<CheckoutDraft>) =>
    store.setState((current) => ({
      ...current,
      checkoutDraft: { ...current.checkoutDraft, ...partial },
    })),
  loadCart: () => {
    store.setState({ cartLoading: true });
    try {
      const currentCart = await ordersApi.currentCart();
      store.setState({ currentCart, cartLoading: false });
      return currentCart;
    } catch {
      store.setState({ currentCart: null, cartLoading: false });
      return null;
    }
  },
  addToCart: async (product: Record<string, unknown>, quantity?: number) => {
    const cart = (await commerceStore.loadCart()) ?? (await ordersApi.currentCart());
    const tiers = product.pricing_tiers as { unit_price?: string }[] | undefined;
    const item = await ordersApi.cartItems.create({
      cart: cart.id,
      sku: product.sku || `SKU-${product.id}`,
      name: product.name,
      quantity: quantity ?? product.minimum_order_quantity ?? 1,
      unit_price: tiers?.[0]?.unit_price || product.unit_price || "0",
    });
    await commerceStore.loadCart();
    return item;
  },
  updateCartItem: async (id: string | number, quantity: number) => {
    await ordersApi.cartItems.update(id, { quantity });
    return commerceStore.loadCart();
  },
  removeCartItem: async (id: string | number) => {
    await ordersApi.cartItems.remove(id);
    return commerceStore.loadCart();
  },
  recalculate: async () => {
    const cart = store.getState().currentCart;
    if (!cart?.id) return null;
    const updated = await ordersApi.carts.action(String(cart.id), "recalculate", {});
    store.setState({ currentCart: updated });
    return updated;
  },
  checkout: async (payload?: Record<string, unknown>) => {
    const cart = store.getState().currentCart ?? (await commerceStore.loadCart());
    if (!cart?.id) throw new Error("Cart is empty");
    const draft = store.getState().checkoutDraft;
    const order = await ordersApi.carts.action(String(cart.id), "checkout", {
      notes: draft.notes,
      requested_delivery_date: draft.requested_delivery_date || undefined,
      payment_terms: draft.payment_terms,
      ...payload,
    });
    store.setState({ selectedOrder: order });
    await commerceStore.loadCart();
    return order;
  },
};
