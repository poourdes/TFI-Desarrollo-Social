import { LayoutDashboard, LogOut, Users } from "lucide-react";
import type { AuthenticatedUser } from "../../api";

type PanelViewKey = "cases" | "users";
export function PanelSidebar({ user, view, onView, onLogout }: { user: AuthenticatedUser; view: PanelViewKey; onView: (v: PanelViewKey) => void; onLogout: () => void }) {
  const item = (id: PanelViewKey, label: string, Icon: typeof LayoutDashboard) => (
    <button
      key={id}
      onClick={() => onView(id)}
      className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium ${view === id ? "bg-brand-700 text-white" : "text-slate-700 hover:bg-slate-100"}`}
    >
      <Icon className="h-4 w-4" aria-hidden="true" /> {label}
    </button>
  );
  return (
    <aside className="rounded-2xl bg-white p-4 shadow-soft ring-1 ring-slate-100">
      <div className="mb-4 border-b border-slate-100 pb-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-brand-800">Cuidar</p>
        <p className="mt-1 font-semibold text-slate-900">{user.full_name}</p>
        <p className="text-xs text-slate-500">{user.email} · {user.role}</p>
      </div>
      <nav className="space-y-1" aria-label="Panel">
        {item("cases", "Casos", LayoutDashboard)}
        {user.role === "admin" && item("users", "Usuarios", Users)}
      </nav>
      <button onClick={onLogout} className="mt-6 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-slate-700 hover:bg-slate-100">
        <LogOut className="h-4 w-4" aria-hidden="true" /> Cerrar sesión
      </button>
    </aside>
  );
}
export type { PanelViewKey };
