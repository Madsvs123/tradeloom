import { useNavigate } from "react-router";
import Stack from "@mui/material/Stack";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { useCollection } from "../../hooks/useCollection";
import { ResourceHub } from "../workspace/ResourceWorkspace";
import { resourcesForModule } from "../../catalog";
import { formatMoney } from "../../utils/format";

export default function ContractsPage() {
  const navigate = useNavigate();
  const { rows, loading, count } = useCollection("/contracts/agreements/");

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Contract lifecycle"
        subtitle="Templates, agreements, clauses, amendments, obligations, and renewals."
        actions={<Button onClick={() => navigate("/workspace/contracts/legal-contracts")}>Open vault</Button>}
      />
      <Card title={`${count} agreements`}>
        <DataTable
          loading={loading}
          rows={rows}
          onRowClick={(row) => navigate(`/contracts/${row.id}`)}
          columns={[
            { key: "number", label: "Number" },
            { key: "title", label: "Title" },
            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            { key: "total", label: "Total", render: (value, row) => formatMoney(value, String(row.currency || "USD")) },
          ]}
        />
      </Card>
      <ResourceHub title="Contract objects" subtitle="Every contracts API collection" items={resourcesForModule("contracts")} />
    </Stack>
  );
}
