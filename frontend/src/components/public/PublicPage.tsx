import { useEffect, useState } from "react";
import { getPublicAreas, type PublicAreasResponse } from "../../api";
import { EmergencyBanner } from "./EmergencyBanner";
import { Hero } from "./Hero";
import { PublicFooter } from "./PublicFooter";
import { QuickExitButton } from "./QuickExitButton";
import { ReportStepper } from "./ReportStepper";
import { TrackReportSection } from "./TrackReportSection";

export function PublicPage({ onGoPanel }: { onGoPanel: () => void }) {
  const [data, setData] = useState<PublicAreasResponse | null>(null);

  useEffect(() => {
    void getPublicAreas().then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="min-h-screen bg-sand-50 text-slate-900">
      <a href="#denuncia" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:rounded bg-white px-3 py-2">Saltar al formulario</a>
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-800">Cuidar</p>
            <p className="text-sm text-slate-600">Municipalidad de Aguilares · Desarrollo Social</p>
          </div>
          <nav aria-label="Principal" className="flex items-center gap-2 text-sm">
            <a href="#denuncia" className="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100">Denunciar</a>
            <a href="#seguimiento" className="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100">Seguimiento</a>
            <button onClick={onGoPanel} className="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100">Panel</button>
          </nav>
        </div>
      </header>
      <Hero />
      <EmergencyBanner notice={data?.notice} lines={data?.emergency_lines ?? []} />
      <main>
        <section id="denuncia" className="py-14">
          <div className="mx-auto max-w-4xl px-4 sm:px-6">
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-slate-900">Realizar una denuncia</h2>
              <p className="mt-2 text-slate-600">Completá los pasos. Podés enviar la denuncia sin identificarte.</p>
            </div>
            <ReportStepper data={data} />
          </div>
        </section>
        <TrackReportSection />
      </main>
      <PublicFooter />
      <QuickExitButton />
    </div>
  );
}
