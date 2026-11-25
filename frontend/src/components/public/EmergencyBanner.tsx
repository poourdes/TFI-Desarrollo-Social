import { AlertTriangle, Phone } from "lucide-react";

interface Props {
  notice?: string;
  lines: Array<{ numero: string; etiqueta: string }>;
}

export function EmergencyBanner({ notice, lines }: Props) {
  return (
    <section
      aria-label="Emergencias"
      className="border-y border-amber-200 bg-amber-50"
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" aria-hidden="true" />
          <p className="text-sm text-amber-950">
            <span className="font-semibold">Esta plataforma no es para emergencias.</span>{" "}
            {notice ?? "Ante un riesgo inmediato, llamá a las líneas de ayuda."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {lines
            .filter((l) => ["911", "144"].includes(l.numero))
            .concat(lines.filter((l) => !["911", "144"].includes(l.numero)))
            .filter((l, i, arr) => arr.findIndex((x) => x.numero === l.numero) === i)
            .slice(0, 3)
            .map((line) => (
              <a
                key={line.numero}
                href={`tel:${line.numero}`}
                className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-sm font-semibold text-amber-900 shadow-sm ring-1 ring-amber-200 hover:bg-amber-100"
              >
                <Phone className="h-4 w-4" aria-hidden="true" />
                {line.numero} <span className="hidden font-normal sm:inline">{line.etiqueta}</span>
              </a>
            ))}
        </div>
      </div>
    </section>
  );
}
