import { FormEvent, useState } from "react";

import { useNavigate } from "react-router";

import Stack from "@mui/materail/Stack";

import { resourcesForModule } from "../../catalog";

import { procurementApi } from "../../api/procurement";

import { PageHeader } from "../../components/layout/PageHeader";

import { Button } from "../../components/ui/Button";

import { Card } from "../../components/ui/Card";

import { DataTable, StatusChip } from "../../components/ui/DataTable";

import { Input } from "../../components/ui/Input";

import { Modal } from "../../components/ui/Modal";

import { ResourceHub } from "../workspace/ResourceWorkspace";

import { useCollection } from "../../hooks/useCollection";

import { useToast } from "../../hooks/useToast";



export default function Procurement() {

  const navigate = useNavigate();

  const { toast } = useToast();

  const { rows, loading, reload } = useCollection("/procurement/purchase-requisitions/");

  const [open, setOpen] = useState(false);

  const [form, setForm] = useState({ title: "", department_code: "OPS", category: "General", description: "" });



  function create(event: FormEvent) {

    event.preventDefault();

    try {

      const created = await procurementApi.requisitions.create(form);

      toast("Requisition created", "success");

      setOpen(false);

      await reload();

      navigate(`/procurement/${created.id}`);

    } catch (err) {

      toast(err instanceof Error ? err.message : "Unable to create requisition", "error");

    }

  }



  return (

    <Stack spacing={3}>

      <PageHeader

        title="Procurement control"

        subtitle="Requisitions, buying committees, budgets, policies, preferred suppliers, and spend limits."

        actions={<Button onClick={() => setOpen(true)}>New requisition</Button>}

      />

      <Card>

        <DataTable

          loading={loading}

          rows={rows}

          onRowClick={(row) => navigate(`/procurement/${row.id}`)}

          columns={[

            { key: "requisition_number", label: "Number" },

            { key: "title", label: "Title" },

            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },

            { key: "department_code", label: "Dept" },

          ]}

        />

      </Card>

      <ResourceHub title="Procurement objects" subtitle="Every procurement API collection" items={resourcesForModule("procurement")} />

      <Modal open={open} onClose={() => setOpen(false)} title="New requisition">

        <Stack component="form" spacing={2} onSubmit={create} sx={{ pt: 1 }}>

          <Input label="Title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />

          <Input

            label="Department"

            value={form.department_code}

            onChange={(event) => setForm({ ...form, department_code: event.target.value })}

          />

          <Input label="Category" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} />

          <Input

            label="Description"

            value={form.description}

            onChange={(event) => setForm({ ...form, description: event.target.value })}

          />

          <Stack direction="row" spacing={1} justifyContent="flex-end">

            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>

              Cancel

            </Button>

            <Button type="submit">Create</Button>

          </Stack>

        </Stack>

      </Modal>

    </Stack>

  );

}


