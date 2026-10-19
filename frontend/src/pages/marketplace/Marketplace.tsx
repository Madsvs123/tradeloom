import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router";
import CardActionArea from "@mui/materail/CardActionArea";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { marketplaceApi } from "../../api/marketplace";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Badge } from "../../components/ui/Badge";
import { useToast } from "../../hooks/useToast";
import { commerceStore } from "../../store/commerceStore";
import { asRows } from "../../utils/format";

export default function Marketplace() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [products, setProducts] = useState<Record<string, unknown>[]>([]);
  const [categories, setCategories] = useState<Record<string, unknown>[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [inStock, setInStock] = useState(false);
  const [minRating, setMinRating] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    const params: Record<string, string> = { search: query, published: "true" };
    if (category) params.category = category;
    if (inStock) params.in_stock = "false";
    if (minRating) params.rating = minRating;
    try {
      const data = await marketplaceApi.search(params);
      setProducts(asRows(data));
    } catch {
      const fallback = await marketplaceApi.products.list(params);
      setProducts(asRows(fallback));
    }
  }

  useEffect(() => {
    marketplaceApi.categories.list().then((data) => setCategories(asRows(data))).catch(() => undefined);
    void load();
  }, []);

  async function saveSearch(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await marketplaceApi.savedSearches.create({
        name: query || "Marketplace search",
        query,
        filters: { category, in_stock: inStock, min_rating: minRating },
      });
      toast("Search saved", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to save search", "error");
    } finally {
      setSaving(false);
    }
  }

  async function addToCart(product: Record<string, unknown>) {
    try {
      await commerceStore.addToCart(product);
      toast("Added to cart", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to add to cart", "error");
    }
  }

  async function publish(product: Record<string, unknown>) {
    try {
      await marketplaceApi.products.action(String(product.id), "publish", {});
      toast("Product published", "success");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Publish failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Marketplace discovery"
        subtitle="Full-text search with category, stock, and supplier rating filters."
        actions={
          <Button variant="secondary" onClick={saveSearch} disabled={saving}>
            Save search
          </Button>
        }
      />
      <Card>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }}>
          <Input label="Search" value={query} onChange={(event) => setQuery(event.target.value)} />
          <Select label="Category" value={category} onChange={(event) => setCategory(event.target.value)}>
            <MenuItem value="">All categories</MenuItem>
            {categories.map((item) => (
              <MenuItem key={String(item.slug ?? item.id)} value={String(item.slug ?? item.name)}>
                {String(item.name)}
              </MenuItem>
            ))}
          </Select>
          <FormControlLabel
            control={<Checkbox checked={inStock} onChange={(event) => setInStock(event.target.checked)} />}
            label="In stock"
          />
          <Input label="Min rating" value={minRating} onChange={(event) => setMinRating(event.target.value)} />
          <Button onClick={() => void load()}>Search</Button>
        </Stack>
      </Card>
      <Grid container spacing={2}>
        {products.map((product) => (
          <Grid item xs={12} sm={6} md={4} key={String(product.id)}>
            <Card>
              <Stack spacing={1.5}>
                <Badge>
                  {String((product.category as { name?: string } | undefined)?.name ?? product.category ?? "Catalog")}
                </Badge>
                <CardActionArea onClick={() => navigate(`/marketplace/${product.id}`)}>
                  <Typography variant="h3">{String(product.name)}</Typography>
                  <Typography color="text.secondary">
                    {String((product.storefront as { name?: string } | undefined)?.name ?? "")}
                  </Typography>
                </CardActionArea>
                <Typography variant="body2">
                  MOQ {String(product.minimum_order_quantity ?? 1)} · {product.is_published ? "Published" : "Draft"}
                </Typography>
                <Stack direction="row" spacing={1}>
                  <Button size="sm" variant="secondary" onClick={() => navigate(`/marketplace/${product.id}`)}>
                    Details
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => void publish(product)}>
                    Publish
                  </Button>
                  <Button size="sm" onClick={() => void addToCart(product)}>
                    Add to cart
                  </Button>
                </Stack>
              </Stack>
            </Card>
          </Grid>
        ))}
      </Grid>
      {!products.length ? <Typography color="text.secondary">No products matched those filters.</Typography> : null}
    </Stack>
  );
}
