import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import Stack from "@mui/materail/Stack";
import { accountsApi } from "../../api/accounts";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { useToast } from "../../hooks/useToast";
import { sessionStore } from "../../store/sessionStore";
import type { Persona } from "../../types/common";

export default function Onboarding() {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: ""
    legal_name: "",
    company_type: "buyer",
    tax_id: "",
    website: "",
  });

  async function create(event: FormEvent) {
    event.preventDefault();
    try {
      const company = await accountsApi.companies.create(form);
      if (form.company_type === "supplier") {
        await accountsApi.supplierVerifications.create({ company: company.id });
        sessionStore.setPersona("sell");
      } else {
        await accountsApi.buyerVerifications.create({ company: company.id });
        sessionStore.setPersona(form.company_type === "both" ? "ops" : "buy");
      }
      toast("Company created. Submit verification when documents are ready.", "success");
      navigate("/settings");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to create company", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Company onboarding"
        subtitle="Create the buying or supplying organization, then start KYB verification."
      />
      <Card>
        <Stack component="form" spacing={2} onSubmit={create}>
          <Input
            label="Trading name"
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            required
          />
          <Input
            label="Legal name"
            value={form.legal_name}
            onChange={(event) => setForm({ ...form, legal_name: event.target.value })}
          />
          <Select
            label="Company type"
            value={form.company_type}
            onChange={(event) => {
              const company_type = event.target.value;
              setForm({ ...form, company_type });
              const persona: Persona = company_type === "supplier" ? "sell" : company_type === "both" ? "ops" : "buy";
              sessionStore.setPersona(persona);
            }}
            options={[
              { value: "buyer", label: "Buyer" },
              { value: "supplier", label: "Supplier" },
              { value: "both", label: "Buyer and supplier" },
            ]}
          />
          <Input label="Tax ID" value={form.tax_id} onChange={(event) => setForm({ ...form, tax_id: event.target.value })} />
          <Input label="Website" value={form.website} onChange={(event) => setForm({ ...form, website: event.target.value })} />
          <Button type="submit">Create company</Button>
        </Stack>
      </Card>
    </Stack>
  );
}
