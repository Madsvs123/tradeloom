import { useEffect, useState } from "react";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { commsApi } from "../../api/comms";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useToast } from "../../hooks/useToast";
import { useWebSocket } from "../../hooks/useWebSocket";
import { sessionStore } from "../../store/sessionStore";
import { asRows, formatDateTime } from "../../utils/format";

export default function Notifications() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const { lastMessage } = useWebSocket("/ws/notification-feed/");

  async function load() {
    const data = await commsApi.notifications.list();
    const results = asRows(data);
    setRows(results);
    sessionStore.setUnread(results.filter((row) => !!row.is_read).length);
  }

  useEffect(() => {
    load().catch(() => toast("Unable to load notifications", "error"));
  }, [toast]);

  useEffect(() => {
    if (lastMessage) void load();
  }, [lastMessage]);

  async function markRead(id: string | number) {
    await commsApi.notifications.action(id, "mark_read", {});
    await load();
  }

  async function markAll() {
    await commsApi.notifications.collectionPost("mark-all-read", {});
    toast("All notifications marked read", "success");
    await load();
  }

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Notifications"
        subtitle="Order, RFQ, dispute, and workflow events across the commercial graph."
        actions={<Button onClick={() => void markAll()}>Mark all read</Button>}
      />
      <Card>
        <Stack spacing={2}>
          {rows.flatMap((row) => (
            <Stack
              key={String(row.id)}
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
              alignItems={{ sm: "center" }}
              justifyContent="space-between"
            >
              <div>
                <Typography fontWeight={700}>{String(row.title ?? row.subject ?? "Notification")}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {String(row.body ?? "")} · {formatDateTime(row.created_at)}
                </Typography>
              </div>
              {!row.is_read ? (
                <Button size="sm" variant="secondary" onClick={() => void markRead(String(row.id))}>
                  Mark read
                </Button>
              ) : (
                <Typography variant="caption" color="text.secondary">
                  Read
                </Typography>
              )}
            </Stack>
          ))}
          {!rows.length ? <Typography color="text.secondary">No notifications yet.</Typography> : null}
        </Stack>
      </Card>
    </Stack>
  );
}
