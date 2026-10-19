import  FormEvent, useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import { accountsApi } from "../../api/accounts";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { useAuth } from "../../hooks/useAuth";
import { useCollection } from "../../hooks/useCollection";
import { useToast } from "../../hooks/useToast";

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const { toast } = useToast();
  const [form, setForm] = useState({ first_name: "", last_name: "", phone_number: "", job_title: "" });
  const companies = useCollection("/accounts/companies/");
  const team = useCollection("/accounts/team-members/");
  const audit = useCollection("/accounts/audit-logs/");

  useEffect(() => {
    if (!user) return;
    setForm({
      first_name: user.first_name ?? "",
      last_name: user.last_name ?? "",
      phone_number: user.phone_number ?? "",
      job_title: user.job_title ?? "",
    });
  }, [user]);

  async function save(event: FormEvent) {
    event.preventDefault();
    try {
      await accountsApi.updateProfile(form);
      await refreshUser();
      toast("Profile updated", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Update failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader title="Settings" subtitle="Profile, companies, team, branches, verification, and audit logs." />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card title="Profile">
            <Stack component="div" spacing={2} onSubmit={save}>
              <Input
                label="First name"
                value={form.first_name}
                onChange={(event) => setForm({ ...form, first_name: event.target.value })}
              />
              <Input
                label="Last name"
                value={form.last_name}
                onChange={(event) => setForm({ ...form, last_name: event.target.value })}
              />
              <Input
                label="Job title"
                value={form.job_title}
                onChange={(event) => setForm({ ...form, job_title: event.target.value })}
              />
              <Input
                label="Phone"
                value={form.phone_number}
                onChange={(event) => setForm({ ...form, phone_number: event.target.value })}
              />
              <Button type="submit">Save profile</Button>
            </Stack>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card title="Companies">
            <DataTable
              loading={companies.loading}
              rows={companies.rows}
              columns={[
                { key: "name", label: "Name" },
                { key: "company_type", label: "Type" },
                { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
              ]}
            />
          </Card>
        </Grid>
      </Grid>
      <Card title="Team">
        <DataTable
          loading={team.loading}
          rows={team.rows}
          columns={[
            { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            { key: "role", label: "Role" },
          ]}
        />
      </Card>
      <Card title="Audit log">
        <DataTable
          loading={audit.loading}
          rows={audit.rows}
          columns={[
            { key: "action", label: "Action" },
            { key: "target_type", label: "Target" },
            { key: "created_at", label: "When" },
          ]}
        />
      </Card>
    </Stack>
  );
}
