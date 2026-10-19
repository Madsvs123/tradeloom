import { FormEvent, useState } from "react";

import { useNavigate } from "react-router-dom";

import Stack from "@mui/material/Stack";

import { procurementApi } from "../../api/procurement";

import { PageHeader } from "../../components/layout/PageHeader";

import { Button } from "../../components/ui/Button";

import { Card } from "../../components/ui/Card";

import { DataTable, StatusChip } from "../../components/ui/DataTable";

import { Input } from "../../components/ui/Input";

import { Modal } from "../../components/ui/Modal";

import { useCollection } from "../../hooks/useCollection";

import { useToast } from "../../hooks/useToast";



export default function Suppliers() {

  const navigate = useNavigate();

  const { toast } = useToast();

  const { rows, loading, reload } = useCollection("/procurement/suppliers/");

  const [open, setOpen] = useState(false);

  const [form, setForm] = useState({ name: "", legal_name: "", category: "", primary_contact_email: "" });



  function create(event: FormEvent) {

    event.preventDefault();

    try {

      await procurementApi.suppliers.create(form);

      toast("Supplier created", "success");

      setOpen(false);

      await reload();

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to create supplier", "error");

    }

  }



  return (

    <Stack spacing={3}>

      <PageHeader

        title="Supplier network"

        subtitle="Verified suppliers with scorecards, risk posture, and commercial capabilities."

        actions={<Button onClick={() => setOpen(true)}>Invite supplier</Button>}

      />

      <Card>

        <DataTable

          loading={loading}

          rows={rows}

          onRowClick={(row) => navigate(`/workspace/procurement/suppliers/${row.id}`)}

          columns={[

            { key: "name", label: "Name" },

            { key: "category", label: "Category" },

            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },

            { key: "risk_rating", label: "Risk" },

          ]}

        />

      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title="Invite supplier">

        <Stack component="form" spacing={2} onSubmit={create} sx={{ pt: 1 }}>

          <Input label="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />

          <Input

            label="Legal name"

            value={form.legal_name}

            onChange={(event) => setForm({ ...form, legal_name: event.target.value })}

          />

          <Input label="Category" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} />

          <Input

            label="Contact email"

            type="email"

            value={form.primary_contact_email}

            onChange={(event) => setForm({ ...form, primary_contact_email: event.target.value })}

          />

          <Stack direction="row" spacing={1} justifyContent="flex-end">

            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>

              Cancel

            </Button>

            <Button type="button">Save</Button>

          </Stack>

        </Stack>

      </Modal>

    </Stack>

  );

}


