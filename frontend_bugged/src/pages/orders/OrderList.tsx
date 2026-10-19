import  useNavigate } from "react-router-dom";

import Stack from "@mui/material/Stack";

import { PageHeader } from "../../components/layout/PageHeader";

import { Card } from "../../components/ui/Card";

import { DataTable, StatusChip } from "../../components/ui/DataTable";

import { useCollection } from "../../hooks/useCollection";

import { formatMoney } from "../../utils/format";



export default function OrderList() 
  const navigate = useNavigate();

  const { rows, loading, count } = useCollection("/orders/orders/");

  return (

    <Stack spacing={3}>

      <PageHeader

        title="Orders"

        subtitle={`${count} purchase orders with approvals, invoices, shipments, returns, and settlements.`}

      />

      <Card>

        <DataTable

          loading={loading}

          rows={rows}

          onRowClick={(row) => navigate(`/orders/${row.id}`)}

          columns={[

            { key: "number", label: "Number" },

            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },

            { key: "total", label: "Total", render: (value, row) => formatMoney(value, String(row.currency ?? "USD")) },

            { key: "requested_delivery_date", label: "Need by" },

          ]}

        />

      </Card>

    </Stack>

  );

}


