import { Copy, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import type { ReportCreated } from "../../api";

export function ConfirmationScreen({ created, onNew }: { created: ReportCreated; onNew: () => void }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(created.tracking_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }
  return (
    <div className="rounded-3xl bg-white p-6 shadow-soft ring-1 ring-slate-100 sm:p-8">
      <div className="flex items-center gap-3 text-brand-700">
        <CheckCircle2 className="h-7 w-7" aria-hidden="true" />
        <h3 className="text-2xl font-semibold text-slate-900">Denuncia recibida</h3>
      </div>
      <p className="mt-3 text-slate-600">Guardá este código. Es la única forma de consultar el estado de la denuncia.</p>
      <div className="mt-6 rounded-2xl bg-brand-50 p-5 ring-1 ring-brand-100">
        <p className="text-sm font-medium text-brand-800">Código de seguimiento</p>
        <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-2xl font-bold tracking-wide text-slate-900">{created.tracking_code}</p>
          <button
            type="button"
            onClick={() => void copy()}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-brand-800 ring-1 ring-brand-200 hover:bg-brand-100"
          >
            <Copy className="h-4 w-4" aria-hidden="true" /> {copied ? "Copiado" : "Copiar"}
          </button>
        </div>
        <p className="mt-3 text-sm text-slate-600">Caso: {created.case_number}</p>
      </div>
      <button type="button" onClick={onNew} className="mt-6 text-sm font-semibold text-brand-700 hover:text-brand-800">
        Realizar otra denuncia
      </button>
    </div>
  );
}
