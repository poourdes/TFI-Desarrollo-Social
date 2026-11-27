import { Briefcase, HeartHandshake, Shield, UserRound, Users } from "lucide-react";
import type { PublicArea } from "../../api";

const icons: Record<string, typeof Shield> = {
  "adultos-mayores": UserRound,
  "violencia-de-genero": Shield,
  "ninez-adolescencia": Users,
  "diversidad-genero": HeartHandshake,
  "abuso-laboral": Briefcase,
};

export function AreaCards({ areas, selected, onSelect }: { areas: PublicArea[]; selected: string; onSelect: (slug: string) => void }) {
  return (
    <div role="radiogroup" aria-label="Área" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {areas.map((area) => {
        const Icon = icons[area.slug] ?? Shield;
        const active = area.slug === selected;
        return (
          <button
            key={area.id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onSelect(area.slug)}
            className={`rounded-2xl border p-4 text-left transition ${active ? "border-muni-celeste border-2 bg-muni-celeste-claro ring-2 ring-muni-celeste/20" : "border-slate-200 bg-white hover:border-muni-celeste/50 hover:bg-muni-celeste-claro/40"}`}
          >
            <Icon className={`h-6 w-6 ${active ? "text-muni-celeste" : "text-slate-500"}`} aria-hidden="true" />
            <div className="mt-3 text-base font-semibold text-muni-navy">{area.nombre}</div>
            <p className="mt-1 text-sm text-slate-600 sm:text-base">{area.descripcion ?? "Denuncias y orientación del área."}</p>
          </button>
        );
      })}
    </div>
  );
}
