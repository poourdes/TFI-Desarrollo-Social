import { useState } from "react";
import { Search } from "lucide-react";
import { trackReport, type TrackingStatusResponse } from "../../api";

const statusLabels: Record<string, string> = { open: "Abierto", in_review: "En revisión", closed: "Cerrado" };
const container = "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8";

export function TrackReportSection() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState<TrackingStatusResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(""); setResult(null);
    try { setResult(await trackReport(code)); }
    catch (err) { setError(err instanceof Error ? err.message : "No se pudo consultar el código."); }
    finally { setLoading(false); }
  }

  return (
    <section id="seguimiento" className="bg-white py-14 sm:py-16">
      <div className={container}>
        <div className="max-w-3xl">
          <h2 className="text-3xl font-semibold text-muni-navy sm:text-4xl">Seguí tu denuncia</h2>
          <p className="mt-2 text-base text-slate-600">Ingresá el código que recibiste al enviar la denuncia.</p>
        </div>
        <form onSubmit={handleSubmit} className="mt-6 flex max-w-3xl flex-col gap-3 sm:flex-row">
          <label className="sr-only" htmlFor="tracking-code">Código de seguimiento</label>
          <input id="tracking-code" value={code} onChange={(e) => setCode(e.target.value)} placeholder="CUID-XXXX-XXXX-XXXX" className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base shadow-sm" required />
          <button type="submit" disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-xl bg-muni-celeste px-5 py-3 text-sm font-semibold text-muni-navy hover:bg-muni-navy hover:text-white disabled:opacity-60 sm:text-base">
            <Search className="h-4 w-4" aria-hidden="true" /> Consultar
          </button>
        </form>
        {error && <p className="mt-4 max-w-3xl rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}
        {result && (
          <div className="mt-6 max-w-3xl rounded-2xl bg-white p-6 shadow-soft ring-1 ring-slate-100">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div><p className="text-sm text-slate-500">Caso</p><p className="font-semibold text-muni-navy">{result.case_number}</p></div>
              <span className="rounded-full bg-muni-celeste-claro px-3 py-1 text-sm font-medium text-muni-navy ring-1 ring-muni-celeste/30">{statusLabels[result.case_status] ?? result.case_status}</span>
            </div>
            <ol className="mt-6 space-y-4 border-l-2 border-muni-celeste/30 pl-5">
              {result.timeline.map((event, idx) => (
                <li key={`${event.created_at}-${idx}`} className="relative">
                  <span className="absolute -left-[1.45rem] mt-1.5 h-3 w-3 rounded-full bg-muni-celeste" />
                  <p className="text-sm text-slate-500">{new Date(event.created_at).toLocaleString("es-AR")}</p>
                  <p className="text-sm text-slate-800 sm:text-base">{event.message}</p>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </section>
  );
}
