import summary from "@/data/summary.json";
import RedTeamChart from "./RedTeamChart";

const VERDICT_COLOR: Record<string, string> = {
  green: "#0a7d28",
  amber: "#d97706",
  red: "#b00020",
};

function Card({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: "0.9rem 1.2rem", minWidth: 180 }}>
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 600, color: color ?? "#1a1a1a" }}>{value}</div>
    </div>
  );
}

export default function Page() {
  const s = summary as typeof summary;
  const redteamRows = Object.entries(s.redteam.by_category).map(([category, ok]) => ({
    category,
    withstood: ok ? 1 : 0,
  }));

  return (
    <main style={{ maxWidth: 920, margin: "0 auto" }}>
      <h1>AI Governance Dashboard</h1>
      <p style={{ color: "#555" }}>
        Live compliance view from the toolkit&apos;s <code>/summary</code> endpoint.
      </p>

      <section style={{ display: "flex", gap: "1rem", flexWrap: "wrap", margin: "1rem 0 2rem" }}>
        <Card
          label="Risk verdict"
          value={s.risk.verdict.toUpperCase()}
          color={VERDICT_COLOR[s.risk.verdict]}
        />
        <Card label="Controls satisfied" value={`${s.risk.satisfied}/${s.risk.total}`} />
        <Card
          label="Red-team pass rate"
          value={`${Math.round(s.redteam.pass_rate * 100)}%`}
          color={s.redteam.pass_rate >= 0.8 ? "#0a7d28" : "#d97706"}
        />
        <Card label="Audit events" value={s.audit_events.toLocaleString()} />
      </section>

      <h2>OWASP LLM red-team — categories withstood</h2>
      <p style={{ color: "#555" }}>
        Green = the guarded target withstood every probe in that category; red = at
        least one attack got through.
      </p>
      <RedTeamChart data={redteamRows} />
    </main>
  );
}
