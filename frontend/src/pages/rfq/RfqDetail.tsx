import  FormEvent, useEffect, useState } from "react";

import { useParams } from "react-router-dom";

import Grid from "@mui/material/Grid";

import Stack from "@mui/material/Stack";

import Typography from "@mui/material/Typography";

import { rfqApi } from "../../api/rfq";

import { PageHeader } from "../../components/layout/PageHeader";

import { Button } from "../../components/ui/Button";

import { Card } from "../../components/ui/Card";

import { StatusChip } from "../../components/ui/DataTable";

import { Textarea } from "../../components/ui/Textarea";

import { useToast } from "../../hooks/useToast";

import { commerceStore } from "../../store/commerceStore";

import { asRows, formatStatus } from "../../utils/format";



export default function RfqDetail() {

  const { id = "" } = useParams();

  const { toast } = useToast();

  const [rfq, setRfq] = useState<Record<string, unknown> | null>(null);

  const [quotes, setQuotes] = useState<Record<string, unknown>[]>([]);

  const [messages, setMessages] = useState<Record<string, unknown>[]>([]);

  const [body, setBody] = useState("");



  async function load() {

    const record = await rfqApi.rfqs.get(id);

    setRfq(record);

    commerceStore.setSelectedRfq(record);

    const quoteData = await rfqApi.quotations.list({ quotation: id });

    setQuotes(asRows(quoteData));

    const messageData = await rfqApi.messages.list({ rfq: id });

    setMessages(asRows(messageData));

  }



  useEffect(() => {

    load().catch(() => toast("Unable to load RFQ", "error"));

  }, [id, toast]);



  async function run(name: string) {

    try {

      const updated = await rfqApi.rfqs.action(id, name, {});

      setRfq(updated);

      commerceStore.setSelectedRfq(updated);

      toast(`${name} completed`, "success");

    } catch (err) {

      toast(err instanceof Error ? err.message : "Action failed", "error");

    }

  }



  async function send(event: FormEvent) {

    event.preventDefault();

    try {

      await rfqApi.messages.create({ rfq: id, body });

      setBody("");

      await load();

    } catch (err) {

      toast(err instanceof Error ? err.message : "Message failed", "error");

    }

  }



  async function quoteAction(quoteId: string, name: string) {

    try {

      await rfqApi.quotations.action(quoteId, name, {});

      toast(`${name} completed`, "success");

      await load();

    } catch (err) {

      toast(err instanceof Error ? err.message : "Quotation action failed", "error");

    }

  }



  if (!rfq) return null;



  return (

    <Stack spacing={3}>

      <PageHeader

        title={String(rfq.reference || rfq.title)}

        subtitle={formatStatus(rfq.status)}

        actions={

          <>

            <Button variant="secondary" onClick={() => void run("issue")}>

              Issue

            </Button>

            <Button variant="danger" onClick={() => void run("decline")}>

              Decline

            </Button>

          </>

        }

      />

      <Grid container spacing={2}>

        <Grid item xs={12} md={6}>

          <Card title="Quotations">

            <Stack spacing={2}>

              {quotes.map((quote) => (

                <Stack

                  key={String(quote.id)}

                  direction={{ xs: "column", sm: "row" }}

                  spacing={2}

                  alignItems={{ sm: "center" }}

                  justifyContent="space-between"

                >

                  <div>

                    <Typography fontWeight={700}>Quote {String(quote.id)}</Typography>

                    <StatusChip value={quote.status} />

                  </div>

                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>

                    <Button size="sm" variant="secondary" onClick={() => void quoteAction(String(quote.id), "submit")}>

                      Submit

                    </Button>

                    <Button size="sm" onClick={() => void quoteAction(String(quote.id), "award")}>

                      Award

                    </Button>

                    <Button size="sm" variant="ghost" onClick={() => void quoteAction(String(quote.id), "reject")}>

                      Reject

                    </Button>

                  </Stack>

                </Stack>

              ))}

              {!quotes.length ? <Typography color="text.secondary">No quotations yet.</Typography> : null}

            </Stack>

          </Card>

        </Grid>

        <Grid item xs={12} md={6}>

          <Card title="Negotiation">

            <Stack spacing={2}>

              {messages.map((message) => (

                <Typography key={String(message.id)} variant="body2">

                  <Typography component="span" fontWeight={700}>

                    {String((message.sender as { email?: string } | undefined)?.email ?? message.sender)}

                  </Typography>{" "}

                  {String(message.body)}

                </Typography>

              ))}

              <Stack component="div" spacing={2} onSubmit={send}>

                <Textarea value={body} onChange={(event) => setBody(event.target.value)} placeholder="Negotiation message" />

                <Button type="button">Send</Button>

              </Stack>

            </Stack>

          </Card>

        </Grid>

      </Grid>

    </Stack>

  );

}


