import { useState } from "react";
import { Search } from "lucide-react";
import { trackReport, type TrackingStatusResponse } from "../../api";

const statusLabels: Record<string, string> = {
  open: "Abierto",
  in_review: "En revisión",
  closed: "Cerrado",
};

export function TrackReportSection() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState<TrackingStatusResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await trackReport(code));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo consultar el código.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="seguimiento" className="py-14">
      <div className="mx-auto max-w-4xl px-4 sm:px-6">
        <h2 className="text-2xl font-semibold text-slate-900">Seguí tu denuncia</h2>
        <p className="mt-2 text-slate-600">Ingresá el código que recibiste al enviar la denuncia.</p>
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3 sm:flex-row">
          <label className="sr-only" htmlFor="tracking-code">Código de seguimiento</label>
          <input
            id="tracking-code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="CUID-XXXX-XXXX-XXXX"
            className="w-full rounded-xl border border-slate-300 px-4 py-3 shadow-sm"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-700 px-5 py-3 font-semibold text-white hover:bg-brand-800 disabled:opacity-60"
          >
            <Search className="h-4 w-4" aria-hidden="true" /> Consultar
          </button>
        </form>
        {error && <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}
        {result && (
          <div className="mt-6 rounded-2xl bg-white p-6 shadow-soft ring-1 ring-slate-100">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm text-slate-500">Caso</p>
                <p className="font-semibold text-slate-900">{result.case_number}</p>
              </div>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-sm font-medium text-brand-800 ring-1 ring-brand-100">
                {statusLabels[result.case_status] ?? result.case_status}
              </span>
            </div>
            <ol className="mt-6 space-y-4 border-l-2 border-brand-100 pl-5">
              {result.timeline.map((event, idx) => (
                <li key={`${event.created_at}-${idx}`} className="relative">
                  <span className="absolute -left-[1.45rem] mt-1.5 h-3 w-3 rounded-full bg-brand-600" />
                  <p className="text-sm text-slate-500">{new Date(event.created_at).toLocaleString("es-AR")}</p>
                  <p className="text-slate-800">{event.message}</p>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </section>
  );
}
