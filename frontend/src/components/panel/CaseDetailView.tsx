import { AlertTriangle } from "lucide-react";
import type { CaseDetail } from "../../api";
import { AreaBadge, StatusBadge } from "./CasesTable";

export function CaseDetailView({
  detail, notes, setNotes, onTransition, onVisit, onConfirm, onReveal, contacts,
}: {
  detail: CaseDetail; notes: string; setNotes: (v: string) => void; onTransition: (target: string) => void;
  onVisit: () => void; onConfirm: () => void; onReveal: (id: string) => void; contacts: Record<string, string>;
}) {
  return (
    <div className="space-y-4">
      <div className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div><h3 className="text-xl font-semibold text-muni-navy">{detail.case_number}</h3><div className="mt-2 flex flex-wrap gap-2"><AreaBadge name={detail.area_name} /><StatusBadge status={detail.status} /></div></div>
          <div className="flex flex-wrap gap-2">
            {detail.allowed_transitions.map((target) => <button key={target} onClick={() => onTransition(target)} className="rounded-xl border border-slate-300 px-3 py-2 text-sm font-semibold text-muni-navy hover:bg-slate-50">Pasar a {target}</button>)}
          </div>
        </div>
      </div>

      {detail.pending_escalation && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 text-amber-700" aria-hidden="true" />
            <div className="flex-1">
              <p className="text-base font-semibold text-amber-950">Escalamiento sugerido</p>
              <p className="text-sm text-amber-900 sm:text-base">El caso alcanzó un umbral configurado. Revisá la situación y confirmá solo si corresponde.</p>
              <button onClick={onConfirm} className="mt-3 rounded-xl bg-amber-700 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-800">Confirmar escalamiento sugerido</button>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
          <h4 className="text-base font-semibold text-muni-navy">Denuncias</h4>
          <div className="mt-4 space-y-4">
            {detail.reports.map((report) => (
              <article key={report.id} className="rounded-xl bg-muni-celeste-claro/30 p-4 ring-1 ring-slate-200">
                <p className="text-sm text-slate-800 whitespace-pre-wrap sm:text-base">{report.description}</p>
                <p className="mt-2 text-sm text-slate-500">{report.locality}{report.address ? ` · ${report.address}` : ""}</p>
                {report.has_contact && <button className="mt-2 text-sm font-semibold text-muni-celeste hover:text-muni-navy hover:underline" onClick={() => onReveal(report.id)}>Ver contacto</button>}
                {contacts[report.id] && <p className="mt-1 text-sm text-slate-700">{contacts[report.id]}</p>}
              </article>
            ))}
          </div>
        </section>
        <section className="space-y-4">
          <div className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
            <h4 className="text-base font-semibold text-muni-navy">Registrar visita</h4>
            <div className="mt-3 flex flex-col gap-2 sm:flex-row">
              <label className="sr-only" htmlFor="visit-notes">Notas de la visita</label>
              <input id="visit-notes" aria-label="Notas de la visita" className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-sm sm:text-base" placeholder="Notas de la visita" value={notes} onChange={(e) => setNotes(e.target.value)} />
              <button onClick={onVisit} className="rounded-xl bg-muni-celeste px-4 py-2 text-sm font-semibold text-muni-navy hover:bg-muni-navy hover:text-white">Registrar visita</button>
            </div>
          </div>
          <div className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
            <h4 className="text-base font-semibold text-muni-navy">Línea de tiempo</h4>
            <ol className="mt-4 space-y-3 border-l-2 border-muni-celeste/30 pl-4">
              {detail.timeline.map((e, i) => (
                <li key={`${e.created_at}-${i}`} className="relative"><span className="absolute -left-[1.2rem] mt-1.5 h-2.5 w-2.5 rounded-full bg-muni-celeste" /><p className="text-sm text-slate-500">{new Date(e.created_at).toLocaleString("es-AR")}</p><p className="text-sm text-slate-700 sm:text-base">{e.message}</p></li>
              ))}
            </ol>
          </div>
        </section>
      </div>
    </div>
  );
}
