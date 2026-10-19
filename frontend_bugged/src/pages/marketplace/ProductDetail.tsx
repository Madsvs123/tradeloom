import { useEffect, useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

import Grid from "@mui/material/Grid";

import Stack from "@mui/material/Stack";

import Typography from "@mui/material/Typography";

import { marketplaceApi } from "../../api/marketplace";

import { PageHeader } from "../../components/layout/PageHeader";

import { Button } from "../../components/ui/Button";

import { Card } from "../../components/ui/Card";

import { useToast } from "../../hooks/useToast";

import { commerceStore } from "../../store/commerceStore";

import { asRows, formatMoney } from "../../utils/format";



export default function ProductDetail() {

  const { id = "" } = useParams();

  const navigate = useNavigate();

  const { toast } = useToast();

  const [product, setProduct] = useState<Record<string, unknown> | null>(null);

  const [reviews, setReviews] = useState<Record<string, unknown>[]>([]);



  useEffect(() => {

    marketplaceApi.products

      .get(id)

      .then((record) => {

        setProduct(record);

        commerceStore.setSelectedProduct(record);

      })

      .catch(() => toast("Product not found", "error"));

    marketplaceApi.reviews.list({ product: id }).then((data) => setReviews(asRows(data))).catch(() => undefined);

  }, [id, toast]);



  if (!product) return null;



  async function save() {

    try {

      await marketplaceApi.products.action(id, "save_product", { notes: "Watching from marketplace" });

      toast("Saved to your list", "success");

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to save", "error");

    }

  }



  async function addToCart() {

    try {

      await commerceStore.addToCart(product);

      toast("Added to cart", "success");

      navigate("/cart");

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to add to cart", "error");

    }

  }



  async function publish() {

    try {

      const updated = await marketplaceApi.products.action(id, product.is_published ? "unpublish" : "publish", {});

      setProduct(updated);

      commerceStore.setSelectedProduct(updated);

      toast(product.is_published ? "Unpublished" : "Published", "success");

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to update listing", "error");

    }

  }



  const tiers = (product.pricing_tiers as Record<string, unknown>[] | undefined) || [];



  return (

    <Stack spacing={3}>

      <PageHeader

        title={String(product.name)}

        subtitle={String((product.storefront as { name?: string } | undefined).name ?? "Supplier catalog")}

        actions={

          <>

            <Button variant="secondary" onClick={() => void save()}>

              Save product

            </Button>

            <Button variant="ghost" onClick={() => void publish()}>

              {product.is_published ? "Unpublish" : "Publish"}

            </Button>

            <Button onClick={() => void addToCart()}>Add to cart</Button>

          </>

        }

      />

      <Grid container spacing={2}>

        <Grid item xs={12} md={6}>

          <Card title="Commercial terms">

            <Stack spacing={2}>

              <Typography>{String(product.description || "No description published.")}</Typography>

              <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>

                <Typography variant="body2">MOQ {String(product.minimum_order_quantity)}</Typography>

                <Typography variant="body2">Unit {String(product.unit)}</Typography>

                <Typography variant="body2">SKU {String(product.sku || "—")}</Typography>

              </Stack>

              <Typography variant="h3">Volume pricing</Typography>

              {tiers.flatMap((tier, index) => (

                <Stack

                  key={index}

                  direction="row"

                  spacing={2}

                  alignItems="center"

                  justifyContent="space-between"

                >

                  <Typography>From {String(tier.min_quantity)}</Typography>

                  <Typography fontWeight={700}>{formatMoney(tier.unit_price, String(tier.currency ?? "USD"))}</Typography>

                </Stack>

              ))}

            </Stack>

          </Card>

        </Grid>

        <Grid item xs={12} md={6}>

          <Card title="Reviews">

            <Stack spacing={2}>

              {reviews.map((review) => (

                <Stack key={String(review.id)} spacing={0.5}>

                  <Typography fontWeight={700}>{String(review.title || `${review.rating}/5`)}</Typography>

                  <Typography variant="body2" color="text.secondary">

                    {String(review.body || "")}

                  </Typography>

                </Stack>

              ))}

              {!reviews.length ? <Typography color="text.secondary">No reviews yet.</Typography> : null}

            </Stack>

          </Card>

        </Grid>

      </Grid>

    </Stack>

  );

}


