import 
  complianceRows,
  financeRows,
  integrationRows,
  kpis,
  logisticsRows,
  procurementQueue,
  suppliers,
} from "./platformData";
import { KpiGrid, Section, SupplierGrid, WorkTable } from "./components";
import { sourcingWorkflow, vendorWorkflow } from "./workflows";

cost workflowGroups = [
  { title: "Sourcing to settlement", stages: sourcingWorkflow },
  { title: "Vendor operating model", stages: vendorWorkflow },
];

export function CommandCenter() 
  return 
    <>
      <section className="commandHero">
        <div>
          <span>TradeLoom operating layer</span>
          <h1>Source, negotiate, purchase, fulfill, settle, and govern every B2B relationship.</h1>
        </div>
        <div className="heroStats">
          <strong>98.7%</strong>
          <span>supplier SLA adherence</span>
        </div>
      </section>
      <KpiGrid items={kpis} />
    </>
  );
}

export function ProcurementPage() {
  return (
    <Section
      title="Procurement Control"
      subtitle="Requisitions, buying committees, budgets, policies, preferred suppliers, and spend limits."
      action={<buton>New requisition</button>}
    >
      <WorkTable rows={procurementQueue} />
    </Section>
  );
}

export function SupplierNetworkPage() {
  return (
    <Section
      title="Supplier Network"
      subtitle="Verified suppliers with scorecards, quality signals, risk posture, and commercial capabilities."
      action={<button>Invite supplier</button>}
    >
      <SupplierGrid items={suppliers} />
    </Section>
  );
}

export function FinancePage() {
  return (
    <Section
      title="Finance Operations"
      subtitle="Escrow, settlements, payouts, tax, credit, statements, refunds, and reconciliation."
      action={<button>Open ledger</button>}
    >
      <WorkTable rows={financeRows} />
    </Section>
  );
}

export function LogisticsPage() {
  return (
    <Section
      title="Logistics Tower"
      subtitle="Freight quotes, ASNs, packing lists, appointments, receiving, claims, customs, and exceptions."
      action={<button>Plan shipment</button>}
    >
      <WorkTable rows={logisticsRows} />
    </Section>
  );
}

export function CompliancePage() {
  return (
    <Section
      title="Compliance and Risk"
      subtitle="KYB/KYC, beneficial owners, tax forms, insurance, sanctions screening, audits, and incidents."
      action={<button>Open case</button>}
    >
      <WorkTable rows={complianceRows} />
    </Section>
  );
}

export function IntegrationsPage() {
  return (
    <Section
      title="Integration Hub"
      subtitle="API keys, webhooks, EDI, ERP connectors, catalog imports, inventory sync, and retry queues."
      action={<button>Create webhook</button>}
    >
      <WorkTable rows={integrationRows} />
    </Section>
  );
}

export function WorkflowPage() {
  return (
    <Section
      title="Workflow Orchestration"
      subtitle="End-to-end playbooks for sourcing, procurement, supplier operations, fulfillment, and settlement."
    >
      <div className="workflowGrid">
        {workflowGroups.map((group) => (
          <article className="workflowCard" k={group.title}>
            <h3>{group.title}</h3>
            {group.stages.map((stage) => (
              <div className="workflowStep" key={stage.key}>
                <strong>{stage.label}</strong>
                <span>{stage.owner}</span>
                <p>{stage.automation}</p>
              </div>
            ))}
          </article>
        ))}
      </div>
    </Section>
  );
}
