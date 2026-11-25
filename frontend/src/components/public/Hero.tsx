import { Lock, Search, ShieldCheck } from "lucide-react";

export function Hero() {
  const guarantees = [
    { icon: ShieldCheck, title: "Anónima por defecto", text: "No pedimos tu identidad para hacer la denuncia." },
    { icon: Search, title: "Código de seguimiento", text: "Te damos un código para consultar el estado." },
    { icon: Lock, title: "Datos cifrados", text: "La información sensible se protege con cifrado." },
  ];
  return (
    <section className="bg-gradient-to-b from-brand-50 to-sand-50 py-12 sm:py-16">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-800">
          Municipalidad de Aguilares · Desarrollo Social
        </p>
        <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
          Denunciá de forma anónima y segura
        </h2>
        <p className="mt-4 max-w-2xl text-base text-slate-700 sm:text-lg">
          Un canal confidencial para informar situaciones que requieren atención del equipo social municipal.
        </p>
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {guarantees.map(({ icon: Icon, title, text }) => (
            <div key={title} className="rounded-2xl bg-white p-5 shadow-soft ring-1 ring-slate-100">
              <Icon className="h-6 w-6 text-brand-700" aria-hidden="true" />
              <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
