import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { getPublicAreas, type PublicAreasResponse } from "../../api";
import { EmergencyBanner } from "./EmergencyBanner";
import { Hero } from "./Hero";
import { PublicFooter } from "./PublicFooter";
import { QuickExitButton } from "./QuickExitButton";
import { ReportStepper } from "./ReportStepper";
import { TrackReportSection } from "./TrackReportSection";

const container = "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8";

export function PublicPage({ onGoPanel }: { onGoPanel: () => void }) {
  const [data, setData] = useState<PublicAreasResponse | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    void getPublicAreas().then(setData).catch(() => setData(null));
  }, []);

  const navItems = (
    <>
      <a href="#seguimiento" onClick={() => setMenuOpen(false)} className="rounded-lg px-3 py-2 text-sm font-medium text-muni-navy hover:bg-muni-celeste-claro">Seguimiento</a>
      <button onClick={() => { setMenuOpen(false); onGoPanel(); }} className="rounded-lg px-3 py-2 text-left text-sm font-medium text-muni-navy hover:bg-muni-celeste-claro">Panel</button>
      <a href="#denuncia" onClick={() => setMenuOpen(false)} className="rounded-lg bg-muni-celeste px-4 py-2 text-sm font-semibold text-muni-navy hover:bg-muni-navy hover:text-white">Denunciar</a>
    </>
  );

  return (
    <div className="min-h-screen bg-white text-muni-navy">
      <a href="#denuncia" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:rounded bg-white px-3 py-2">Saltar al formulario</a>
      <header className="border-b-2 border-muni-celeste bg-white">
        <div className={`${container} flex items-center justify-between gap-4 py-4`}>
          <div className="flex min-w-0 items-center gap-3">
            <img src="/escudo-aguilares.png" alt="Escudo de Aguilares" className="h-12 w-auto shrink-0" />
            <div className="min-w-0">
              <p className="text-lg font-bold leading-tight text-muni-navy">Cuidar</p>
              <p className="truncate text-sm text-slate-600">Municipalidad de Aguilares · Desarrollo Social</p>
            </div>
          </div>
          <nav aria-label="Principal" className="hidden items-center gap-2 md:flex">{navItems}</nav>
          <button className="rounded-lg p-2 text-muni-navy hover:bg-muni-celeste-claro md:hidden" aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"} aria-expanded={menuOpen} onClick={() => setMenuOpen((v) => !v)}>
            {menuOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </button>
        </div>
        {menuOpen && <nav aria-label="Principal móvil" className={`${container} flex flex-col gap-2 border-t border-slate-100 py-4 md:hidden`}>{navItems}</nav>}
      </header>
      <Hero />
      <EmergencyBanner notice={data?.notice} lines={data?.emergency_lines ?? []} />
      <main>
        <section id="denuncia" className="bg-muni-celeste-claro py-14 sm:py-16">
          <div className={container}>
            <div className="mb-8 max-w-3xl">
              <h2 className="text-3xl font-semibold text-muni-navy sm:text-4xl">Realizar una denuncia</h2>
              <p className="mt-2 text-base text-slate-700">Completá los pasos. Podés enviar la denuncia sin identificarte.</p>
            </div>
            <div className="grid gap-6 lg:grid-cols-3 lg:items-start">
              <div className="lg:col-span-2"><ReportStepper data={data} /></div>
              <aside className="space-y-4 lg:sticky lg:top-6">
                <div className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
                  <h3 className="text-base font-semibold text-muni-navy">Cómo funciona</h3>
                  <ol className="mt-3 space-y-2 text-sm text-slate-600">
                    <li><span className="font-medium text-muni-navy">1.</span> Elegí el área y describí la situación.</li>
                    <li><span className="font-medium text-muni-navy">2.</span> Enviá la denuncia con o sin contacto.</li>
                    <li><span className="font-medium text-muni-navy">3.</span> Guardá tu código para seguir el caso.</li>
                  </ol>
                </div>
                <div className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-amber-200">
                  <h3 className="text-base font-semibold text-muni-navy">Líneas de ayuda</h3>
                  <div className="mt-3 space-y-2 text-sm">
                    {(data?.emergency_lines ?? []).slice(0, 3).map((l) => (
                      <a key={l.numero} href={`tel:${l.numero}`} className="block rounded-lg bg-muni-celeste-claro px-3 py-2 font-medium text-muni-navy hover:bg-muni-celeste/20">{l.numero} <span className="font-normal text-slate-700">· {l.etiqueta}</span></a>
                    ))}
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </section>
        <TrackReportSection />
      </main>
      <PublicFooter />
      <QuickExitButton />
    </div>
  );
}
