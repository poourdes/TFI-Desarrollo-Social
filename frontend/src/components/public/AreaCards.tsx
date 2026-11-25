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
    <div role="radiogroup" aria-label="Área" className="grid gap-3 sm:grid-cols-2">
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
            className={`rounded-2xl border p-4 text-left transition ${active ? "border-brand-600 bg-brand-50 ring-2 ring-brand-200" : "border-slate-200 bg-white hover:border-brand-200 hover:bg-sand-50"}`}
          >
            <Icon className={`h-6 w-6 ${active ? "text-brand-700" : "text-slate-500"}`} aria-hidden="true" />
            <div className="mt-3 font-semibold text-slate-900">{area.nombre}</div>
            <p className="mt-1 text-sm text-slate-600">{area.descripcion ?? "Denuncias y orientación del área."}</p>
          </button>
        );
      })}
    </div>
  );
}
