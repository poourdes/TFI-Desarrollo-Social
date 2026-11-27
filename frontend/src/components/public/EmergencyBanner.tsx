import { AlertTriangle, Phone } from "lucide-react";

interface Props {
  notice?: string;
  lines: Array<{ numero: string; etiqueta: string }>;
}

const container = "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8";

export function EmergencyBanner({ lines }: Props) {
  const shown = lines
    .filter((l) => ["911", "144", "102"].includes(l.numero))
    .concat(lines.filter((l) => !["911", "144", "102"].includes(l.numero)))
    .filter((l, i, arr) => arr.findIndex((x) => x.numero === l.numero) === i)
    .slice(0, 3);
  return (
    <section aria-label="Emergencias" className="border-y border-amber-200 bg-amber-50">
      <div className={`${container} grid gap-4 py-4 lg:grid-cols-[1fr_auto] lg:items-center`}>
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" aria-hidden="true" />
          <p className="text-sm text-amber-950 sm:text-base">
            <span className="font-semibold">Esta plataforma no es para emergencias.</span> Ante un riesgo inmediato, llamá a las líneas de ayuda.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:flex lg:flex-wrap">
          {shown.map((line) => (
            <a
              key={line.numero}
              href={`tel:${line.numero}`}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-3 py-2 text-sm font-semibold text-muni-navy shadow-sm ring-1 ring-amber-200 hover:bg-amber-100"
            >
              <Phone className="h-4 w-4 text-amber-700" aria-hidden="true" />
              {line.numero} <span className="font-normal text-slate-700">{line.etiqueta}</span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
