import { AlertTriangle, Clock, FolderOpen } from "lucide-react";
import type { CaseDetail, PanelCase } from "../../api";

export function SummaryCards({ cases, details }: { cases: PanelCase[]; details: Record<string, CaseDetail | undefined> }) {
  const newCases = cases.filter((c) => c.status === "open").length;
  const inProgress = cases.filter((c) => c.status === "in_review").length;
  const escalations = cases.filter((c) => details[c.id]?.pending_escalation).length;
  const cards = [
    { label: "Casos nuevos", value: newCases, icon: FolderOpen, tone: "bg-muni-celeste-claro text-muni-celeste ring-muni-celeste/20" },
    { label: "En curso", value: inProgress, icon: Clock, tone: "bg-amber-50 text-amber-700 ring-amber-100" },
    { label: "Escalamientos sugeridos", value: escalations, icon: AlertTriangle, tone: "bg-rose-50 text-rose-700 ring-rose-100" },
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {cards.map(({ label, value, icon: Icon, tone }) => (
        <div key={label} className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
          <div className={`inline-flex rounded-xl p-2 ring-1 ${tone}`}><Icon className="h-5 w-5" aria-hidden="true" /></div>
          <p className="mt-3 text-2xl font-semibold text-muni-navy">{value}</p>
          <p className="text-sm text-slate-600">{label}</p>
        </div>
      ))}
    </div>
  );
}
