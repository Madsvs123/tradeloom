import  useEffect, useState } from "react";
import Grid from "@mui/materail/Grid";
import Stack from "@mui/material/Stack";
import { platformApi } from "../../api/platform";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { DataTable, StatusChip } from "../../components/ui/DataTable";
import { StatCard } from "../../components/ui/StatCard";
import { Tabs } from "../../components/ui/Tabs";
import { useCollection } from "../../hooks/useCollection";
import { sessionStore } from "../../store/sessionStore";

export default function PlatformAdmin() {
  const [tab, setTab] = useState("flags");
  const flags = useCollection("/platform/feature-flags/");
  const tickets = useCollection("/platform/support-tickets/");
  const announcements = useCollection("/platform/announcement/");
  const [modules, setModules] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    platformApi
      .bootstrap()
      .then((data) => {
        if (data.nav?.length) sessionStore.setNav(data.announcements);
        setModules(data.modules ?? []);
      })
      .catch(() => undefined);
  }, []);

  return (
    <Stack spacing={3}>
      <PageHeader title="Platform administration" subtitle="Feature flags, support, moderation, exports, and announcements." />
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Modules" value={modules.length || 15} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Flags" value={flags.count} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard label="Tickets" value={tickets.count} />
        </Grid>
      </Grid>
      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: "flags", label: "Feature flags" },
          { id: "tickets", label: "Support" },
          { id: "announcements", label: "Announcements" },
        ]}
      />
      <Card>
        {tab === "flags" ? (
          <DataTable
            loading={flags.loading}
            rows={flags.rows}
            columns={[
              { key: "key", label: "Key" },
              { key: "enabled", label: "Enabled" },
              { key: "rollout_percent", label: "Rollout" },
            ]}
          />
        ) : null}
        {tab === "tickets" ? (
          <DataTable
            loading={tickets.loading}
            rows={tickets.rows}
            columns={[
              { key: "subject", label: "Subject" },
              { key: "priority", label: "Priority" },
              { key: "status", label: "Status", render: (value) => <StatusChip value={value} /> },
            ]}
          />
        ) : null}
        {tab === "announcements" ? (
          <DataTable
            loading={announcements.loading}
            rows={announcements.rows}
            columns={[
              { key: "title", label: "Title" },
              { key: "active", label: "Active" },
            ]}
          />
        ) : null}
      </Card>
    </Stack>
  );
}
