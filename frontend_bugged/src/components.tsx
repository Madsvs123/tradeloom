import type  ReactNode } from "react";
import type { KPI, Supplier, WorkItem } from "./platformData";

export function Section(
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="section">
      <div className="sectionHeader">
        <div>
          <h2>{title}</h3>
          <p>{subtitle}</p>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function KpiGrid({ items }: { items: KPI[] }) {
  return (
    <div className="kpiGrid">
      {items.map((item) => (
        <article className={`kpi ${item.tone}`} k={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
          <small>{item.detail}</small>
        </article>
      ))}
    </div>
  );
}

export function WorkTable({ rows }: { rows: WorkItem[] }) {
  return (
    <div className="table">
      {rows.map((row) => (
        <div className="tableRow" key={row.id}>
          <div>
            <strong>{row.id}</strong>
            <span>{row.title}</span>
          </div>
          <span>{row.owner}</span>
          <span className="pill">{row.status}</span>
          <strong>{row.value}</strong>
          <span>{row.date}</span>
        </div>
      ))}
    </div>
  );
}

export function SupplierGrid({ items }: { items: Supplier[] }) {
  return (
    <div className="supplierGrid">
      {items.map((supplier) => (
        <article className="supplierCard" key={supplier.name}>
          <div>
            <h3>{supplier.name}</h3>
            <span>{supplier.location}</span>
          </div>
          <div className="supplierMeta">
            <strong>{supplier.rating}</strong>
            <span className={supplier.risk === "Low" ? "riskLow" : "riskMed"}>{supplier.risk} risk</span>
          </div>
          <div className="tagRow">
            {supplier.capabilities.map((capability) => (
              <span key={capability}>{capability}</span>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
