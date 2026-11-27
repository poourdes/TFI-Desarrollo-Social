import { Lock, Search, ShieldCheck } from "lucide-react";

const container = "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8";

export function Hero() {
  const guarantees = [
    { icon: ShieldCheck, title: "Anónima por defecto", text: "No pedimos tu identidad para hacer la denuncia." },
    { icon: Search, title: "Código de seguimiento", text: "Te damos un código para consultar el estado." },
    { icon: Lock, title: "Datos cifrados", text: "La información sensible se protege con cifrado." },
  ];
  return (
    <section className="flex min-h-[60vh] items-center bg-gradient-to-br from-muni-navy via-muni-navy to-muni-celeste/70 py-16 text-white sm:py-20">
      <div className={container}>
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-12">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-muni-celeste-claro">
              Municipalidad de Aguilares · Desarrollo Social
            </p>
            <h2 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-white md:text-5xl xl:text-6xl">
              Denunciá de forma anónima y segura
            </h2>
            <p className="mt-5 max-w-2xl text-base text-slate-100 sm:text-lg">
              Un canal confidencial para informar situaciones que requieren atención del equipo social municipal.
            </p>
            <a href="#denuncia" className="mt-8 inline-flex rounded-xl bg-muni-celeste px-6 py-3 text-sm font-semibold text-muni-navy hover:bg-white sm:text-base">
              Realizar una denuncia
            </a>
          </div>
          <div className="grid gap-4">
            {guarantees.map(({ icon: Icon, title, text }) => (
              <div key={title} className="flex gap-4 rounded-2xl bg-white p-5 text-muni-navy shadow-soft ring-1 ring-white/20">
                <Icon className="mt-0.5 h-6 w-6 shrink-0 text-muni-celeste" aria-hidden="true" />
                <div>
                  <h3 className="text-base font-semibold">{title}</h3>
                  <p className="mt-1 text-sm text-slate-600 sm:text-base">{text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
