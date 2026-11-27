import type { PanelCase } from "../../api";

const statusStyle: Record<string, string> = {
  open: "bg-sky-50 text-sky-800 ring-sky-200",
  in_review: "bg-amber-50 text-amber-800 ring-amber-200",
  closed: "bg-slate-100 text-slate-700 ring-slate-200",
};
const statusLabel: Record<string, string> = { open: "Abierto", in_review: "En revisión", closed: "Cerrado" };

export function StatusBadge({ status }: { status: string }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${statusStyle[status] ?? "bg-slate-100 text-slate-700 ring-slate-200"}`}>{statusLabel[status] ?? status}</span>;
}
export function AreaBadge({ name }: { name: string }) {
  return <span className="inline-flex rounded-full bg-muni-celeste-claro px-2.5 py-1 text-xs font-medium text-muni-navy ring-1 ring-muni-celeste/30">{name}</span>;
}

export function CasesTable({ cases, onOpen }: { cases: PanelCase[]; onOpen: (id: string) => void }) {
  return (
    <>
      <div className="hidden overflow-x-auto rounded-2xl bg-white shadow-soft ring-1 ring-slate-100 md:block">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr><th className="px-4 py-3 font-medium">Caso</th><th className="px-4 py-3 font-medium">Área</th><th className="px-4 py-3 font-medium">Estado</th><th className="px-4 py-3 font-medium">Denuncias</th><th className="px-4 py-3 font-medium">Fecha</th></tr>
          </thead>
          <tbody>
            {cases.map((item) => (
              <tr key={item.id} className="border-t border-slate-100 hover:bg-muni-celeste-claro/40">
                <td className="px-4 py-3"><button className="font-semibold text-muni-celeste hover:text-muni-navy hover:underline" onClick={() => onOpen(item.id)}>{item.case_number}</button></td>
                <td className="px-4 py-3"><AreaBadge name={item.area_name} /></td>
                <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                <td className="px-4 py-3 text-slate-600">{item.report_count}</td>
                <td className="px-4 py-3 text-slate-600">{new Date(item.created_at).toLocaleDateString("es-AR")}</td>
              </tr>
            ))}
            {cases.length === 0 && <tr><td className="px-4 py-8 text-center text-sm text-slate-500" colSpan={5}>No hay casos para mostrar.</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="grid gap-3 md:hidden">
        {cases.map((item) => (
          <button key={item.id} onClick={() => onOpen(item.id)} className="rounded-2xl bg-white p-4 text-left shadow-soft ring-1 ring-slate-100">
            <div className="flex items-start justify-between gap-3">
              <div><p className="font-semibold text-muni-celeste">{item.case_number}</p><p className="text-sm text-slate-600">{new Date(item.created_at).toLocaleDateString("es-AR")}</p></div>
              <StatusBadge status={item.status} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2"><AreaBadge name={item.area_name} /><span className="text-sm text-slate-600">{item.report_count} denuncias</span></div>
          </button>
        ))}
        {cases.length === 0 && <div className="rounded-2xl bg-white p-6 text-center text-sm text-slate-500 shadow-soft ring-1 ring-slate-100">No hay casos para mostrar.</div>}
      </div>
    </>
  );
}
