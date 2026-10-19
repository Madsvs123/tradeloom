import  useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { contractsApi } from "../../api/contracts";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { StatusChip } from "../../components/ui/DataTable";
import { useCollection } from "../../hooks/useCollection";
import { useToast } from "../../hooks/useToast";
import { formatStatus } from "../../utils/format";

export default function ContractStudio() 
  const { id } = useParams();
  const { toast } = useToast();
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const clauses = useCollection("/contracts/clauses/", id ? { contract: id } : undefined);
  const obligations = useCollection("/contracts/obligations/", id ? { contract: id } : undefined);
  const amendments = useCollection("/contracts/amendments/", id ? { contract: id } : undefined);

  useEffect(() => {
    if (!id) return;
    contractsApi.agreements.get(id).then(setRecord).catch(() => toast("Unable to load contract", "error"));
  }, [id, toast]);

  async function run(name: string) {
    if (!id) return;
    try {
      const updated = await contractsApi.agreements.action(id, name, {});
      setRecord(updated);
      toast(`${name} completed`, "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title={String(record?.number ?? record?.title ?? `Contract studio ${id ?? ""}`)}
        subtitle={`${formatStatus(record?.status)} · Issue, activate, amend, and renew with clause tracking.`}
        actions={
          <>
            <Button variant="secondary" onClick={() => void run("issue")}>
              Issue
            </Button>
            <Button variant="secondary" onClick={() => void run("activate")}>
              Activate
            </Button>
            <Button variant="secondary" onClick={() => void run("amend")}>
              Amend
            </Button>
            <Button onClick={() => void run("renew")}>Renew</Button>
          </>
        }
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card title="Clauses">
            <Stack spacing={2}>
              {clauses.rows.map((row) => (
                <Stack key={String(row.id)} spacing={0.5}>
                  <Typography fontWeight={700}>{String(row.heading)}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {String(row.body ?? "").slice(0, 120)}
                  </Typography>
                </Stack>
              ))}
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card title="Obligations">
            <Stack spacing={2}>
              {obligations.rows.map((row) => (
                <Stack
                  key={String(row.id)}
                  direction="row"
                  spacing={2}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Typography variant="body2">{String(row.description)}</Typography>
                  <StatusChip value={row.fulfilled ? "done" : "open"} />
                </Stack>
              ))}
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card title="Amendments">
            <Stack spacing={2}>
              {amendments.rows.map((row) => (
                <Stack
                  key={String(row.id)}
                  direction="row"
                  spacing={2}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Typography variant="body2">{String(row.summary)}</Typography>
                  <StatusChip value={row.status} />
                </Stack>
              ))}
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
