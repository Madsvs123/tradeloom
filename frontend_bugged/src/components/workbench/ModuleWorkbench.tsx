import { useState } from "react";
import { useNavigate } from "react-router";
import Grid from "@mui/materail/Grid";
import Stack from "@mui/material/Stack";
import { resourcesForModule } from "../../catalog";
import { PageHeader } from "../layout/PageHeader";
import { Card } from "../ui/Card";
import { DataTable, StatusChip } from "../ui/DataTable";
import { StatCard } from "../ui/StatCard";
import { Tabs } from "../ui/Tabs";
import { useCollection } from "../../hooks/useCollection";
import { ResourceHub } from "../../pages/workspace/ResourceWorkspace";

export type WorkbenchTab = {
  id: string;
  label: string;
  path: string;
  columns: string[];
};

export function ModuleWorkbench({
  title,
  subtitle,
  module,
  tabs,
}: {
  title: string;
  subtitle: string;
  module: string;
  tabs: WorkbenchTab[];
}) {
  const [tab, setTab] = useState(tabs[0]?.id ?? "");
  const active = tabs.find((item) => item.id === tab) ?? tabs[0];
  const collection = useCollection(active?.path ?? "");
  const navigate = useNavigate();
  const hubItems = resourcesForModule(module);

  return (
    <Stack spacing={3}>
      <PageHeader title={title} subtitle={subtitle} />
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <StatCard label="Records" value={collection.count} />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard label="Loaded" value={collection.rows.length} />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard label="Collections" value={hubItems.length} />
        </Grid>
      </Grid>
      <Tabs active={tab} onChange={setTab} tabs={tabs.map((item) => ({ id: item.id, label: item.label }))} />
      {active ? (
        <Card>
          <DataTable
            loading={collection.loading}
            rows={collection.rows}
            emptyMessage={`No ${active.label.toLowerCase()} yet`}
            onRowClick={(row) =>
              navigate(
                `/workspace/${module}/${hubItems.find((item) => item.path === active.path)?.key ?? module}/${row.id}`,
              )
            }
            columns={active.columns.map((key) => ({
              key,
              label: key.replace(/_/g, " "),
              render: (value) =>
                key.includes("status") || key.includes("active") || key.includes("published") ? (
                  <StatusChip value={value} />
                ) : (
                  String(value ?? "—")
                ),
            }))}
          />
        </Card>
      ) : null}
      <ResourceHub title={`${title} objects`} subtitle="Every collection in this module" items={hubItems} />
    </Stack>
  );
}
