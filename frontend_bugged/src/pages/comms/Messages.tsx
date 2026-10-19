import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import Grid from "@mui/materail/Grid";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { commsApi } from "../../api/comms";
import { PageHeader } from "../../components/layout/PageHeader";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Textarea } from "../../components/ui/Textarea";
import { useToast } from "../../hooks/useToast";
import { useWebSocket } from "../../hooks/useWebSocket";
import { asRows } from "../../utils/format";

export default function Messages() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [conversations, setConversations] = useState<Record<string, unknown>[]>([]);
  const [messages, setMessages] = useState<Record<string, unknown>[]>([]);
  const [body, setBody] = useState("");
  const { lastMessage, send, connected } = useWebSocket(id ? `/ws/conversations/${id}/` : null);

  async function loadConversations() {
    const data = await commsApi.conversations.list();
    setConversations(asRows(data));
  }

  async function loadMessages(conversationId: string) {
    const data = await commsApi.conversationMessages(conversationId);
    setMessages(Array.isArray(data) ? data : asRows(data));
  }

  useEffect(() => {
    loadConversations().catch(() => toast("Unable to load conversations", "error"));
  }, [toast]);

  useEffect(() => {
    if (id) loadMessages(id).catch(() => undefined);
  }, [id]);

  useEffect(() => {
    if (!lastMessage || typeof lastMessage !== "object") return;
    const payload = lastMessage as { type?: string; message?: Record<string, unknown> };
    if (payload.type === "message.created" && payload.message) {
      setMessages((current) => [...current, payload.message as Record<string, unknown>]);
    }
  }, [lastMessage]);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!id) return;
    try {
      if (connected) {
        send({ action: "send_message", body });
      } else {
        await commsApi.sendConversationMessage(id, { body });
        await loadMessages(id);
      }
      setBody("");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Send failed", "error");
    }
  }

  return (
    <Stack spacing={3}>
      <PageHeader title="Messages" subtitle="Realtime conversations, order discussions, and dispute threads." />
      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Card title="Conversations">
            <List disablePadding>
              {conversations.map((item) => (
                <ListItemButton key={String(item.id)} onClick={() => navigate(`/messages/${item.id}`)} selected={id === String(item.id)}>
                  <ListItemText primary={String(item.subject ?? `Conversation ${item.id}`)} />
                </ListItemButton>
              ))}
            </List>
            {!conversations.length ? <Typography color="text.secondary">No conversations yet.</Typography> : null}
          </Card>
        </Grid>
        <Grid item xs={12} md={7}>
          <Card title={id ? `Thread ${id} ${connected ? "· live" : ""}` : "Select a conversation"}>
            <Stack spacing={2}>
              {messages.map((message) => (
                <Typography key={String(message.id)} variant="body2">
                  <Typography component="span" fontWeight={700}>
                    {String(message.sender ?? "")}
                  </Typography>{" "}
                  {String(message.body ?? message.content ?? "")}
                </Typography>
              ))}
              {id ? (
                <Stack component="form" spacing={2} onSubmit={sendMessage}>
                  <Textarea value={body} onChange={(event) => setBody(event.target.value)} placeholder="Write a message" />
                  <Button type="submit">Send</Button>
                </Stack>
              ) : null}
            </Stack>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
