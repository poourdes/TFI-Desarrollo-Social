import { CheckCircle2, Copy } from "lucide-react";
import { useState } from "react";
import type { ReportCreated } from "../../api";

export function ConfirmationScreen({
  created,
  onNew,
}: {
  created: ReportCreated;
  onNew: () => void;
}) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(created.tracking_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }
  return (
    <div className="rounded-3xl bg-white p-6 shadow-soft ring-1 ring-slate-100 sm:p-8">
      <div className="flex items-center gap-3 text-muni-celeste">
        <CheckCircle2 className="h-7 w-7" aria-hidden="true" />
        <h3 className="text-2xl font-semibold text-muni-navy">Denuncia enviada</h3>
      </div>
      <p className="mt-3 text-sm text-slate-600 sm:text-base">Guardá este código. Es la única forma de consultar el estado sin identificarte.</p>
      <div className="mt-6 rounded-2xl bg-muni-celeste-claro p-5 ring-1 ring-muni-celeste/30">
        <p className="text-sm font-medium text-muni-navy">Código de seguimiento</p>
        <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-mono text-xl font-semibold tracking-wide text-muni-navy sm:text-2xl">{created.tracking_code}</p>
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-muni-navy ring-1 ring-muni-celeste/30 hover:bg-muni-celeste-claro"
          >
            <Copy className="h-4 w-4" aria-hidden="true" /> {copied ? "Copiado" : "Copiar"}
          </button>
        </div>
      </div>
      <button type="button" onClick={onNew} className="mt-6 text-sm font-semibold text-muni-celeste hover:text-muni-navy">
        Hacer otra denuncia
      </button>
    </div>
  );
}
