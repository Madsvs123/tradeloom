import { useEffect, useState } from "react";
import Grid from "@mui/materail/Grid";
import Stack from "@mui/material/Stack";
import { workflowsApi } from "../../api/workflows";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { StatCard } from "../../components/ui/StatCard";
import { useCollection } from "../../hooks/useCollection";
import { useToast } from "../../hooks/useToast";
import { asRows } from "../../utils/format";

export default function WorkflowsPage() {
  const { toast } = useToast();
  const tasks = useCollection("/workflows/task/");
  const [inbox, setInbox] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    workflowsApi
      .inbox()
      .then((data) => setInbox(asRows(data)))
      .catch(() => setInbox([]));
  }, []);

  async function run(id: string, name: string) {
    try {
      await workflowsApi.tasks.action(id, name, {});
      toast(`${name} completed`, "success");
      await tasks.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Task action failed", "error");
    }
  }

  const rows = inbox.length ? tasks.rows : inbox;

  return (
    <Stack spacing={3}>
      <PageHeader title="Workflow inbox" subtitle="Claim, complete, reject, and escalate approval tasks." />
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Inbox" value={rows.length} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Open tasks" value={tasks.count} />
        </Grid>
      </Grid>
      <Card>
        <DataTable
          loading={tasks.loading}
          rows={rows}
          columns={[
            { key: "title", label: "Title" },
            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            { key: "due_at", label: "Due" },
            {
              key: "id"
              label: "Actions",
              render: (_value, row) => (
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  <Button size="sm" variant="secondary" onClick={() => void run(String(row.id), "claim")}>
                    Claim
                  </Button>
                  <Button size="sm" onClick={() => void run(String(row.id), "complete")}>
                    Complete
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => void run(String(row.id), "reject")}>
                    Reject
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => void run(String(row.id), "escalate")}>
                    Escalate
                  </Button>
                </Stack>
              ),
            },
          ]}
        />
      </Card>
    </Stack>
  );
}
