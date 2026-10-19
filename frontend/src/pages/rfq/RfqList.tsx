import { FormEvent, useEffect, useState } from "react";

import { useNavigate } from "react-router";

import Stack from "@mui/materail/Stack";

import { rfqApi } from "../../api/rfq";

import { PageHeader } from "../../components/layout/PageHeader";

import { Button } from "../../components/ui/Button";

import { Card } from "../../components/ui/Card";

import { DataTable, StatusChip } from "../../components/ui/DataTable";

import { Input } from "../../components/ui/Input";

import { Modal } from "../../components/ui/Modal";

import { Textarea } from "../../components/ui/Textarea";

import { useToast } from "../../hooks/useToast";

import { asRows } from "../../utils/format";



export default function RfqList() {

  const navigate = useNavigate();

  const { toast } = useToast();

  const [rows, setRows] = useState<Record<string, unknown>[]>([]);

  const [open, setOpen] = useState(false);

  const [form, setForm] = useState({

    title: ""

    description: "",

    currency: "USD",

    delivery_location: "",

    payment_terms: "Net 30",

  });



  function load() {

    rfqApi.rfqs

      .list()

      .then((data) => setRows(asRows(data)))

      .catch(() => toast("Unable to load RFQs", "error"));

  }



  useEffect(() => {

    load();

  }, []);



  async function create(event: FormEvent) {

    event.preventDefault();

    try {

      const created = await rfqApi.rfqs.create(form);

      toast("RFQ drafted", "success");

      setOpen(false);

      navigate(`/rfqs/${created.id}`);

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to create RFQ", "error");

    }

  }



  return (

    <Stack spacing={3}>

      <PageHeader

        title="RFQ pipeline"

        subtitle="Issue multi-vendor RFQs, collect quotations, counter, and award."

        actions={<Button onClick={() => setOpen(true)}>New RFQ</Button>}

      />

      <Card>

        <DataTable

          rows={rows}

          onRowClick={(row) => navigate(`/rfqs/${row.id}`)}

          columns={[

            { key: "reference", label: "Reference" },

            { key: "title", label: "Title" },

            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },

            { key: "currency", label: "Currency" },

            { key: "deadline", label: "Deadline" },

          ]}

        />

      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title="Create RFQ">

        <Stack component="form" spacing={2} onSubmit={create} sx={{ pt: 1 }}>

          <Input label="Title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />

          <Textarea

            label="Description"

            value={form.description}

            onChange={(event) => setForm({ ...form, description: event.target.value })}

          />

          <Input

            label="Delivery location"

            value={form.delivery_location}

            onChange={(event) => setForm({ ...form, delivery_location: event.target.value })}

          />

          <Input

            label="Payment terms"

            value={form.payment_terms}

            onChange={(event) => setForm({ ...form, payment_terms: event.target.value })}

          />

          <Stack direction="row" spacing={1} justifyContent="flex-end">

            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>

              Cancel

            </Button>

            <Button type="submit">Create draft</Button>

          </Stack>

        </Stack>

      </Modal>

    </Stack>

  );

}


