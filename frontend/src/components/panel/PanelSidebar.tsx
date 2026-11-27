import { LayoutDashboard, LogOut, Menu, Users, X } from "lucide-react";
import { useState } from "react";
import type { AuthenticatedUser } from "../../api";

type PanelViewKey = "cases" | "users";
export function PanelSidebar({ user, view, onView, onLogout }: { user: AuthenticatedUser; view: PanelViewKey; onView: (v: PanelViewKey) => void; onLogout: () => void }) {
  const [open, setOpen] = useState(false);
  const item = (id: PanelViewKey, label: string, Icon: typeof LayoutDashboard) => (
    <button key={id} onClick={() => { onView(id); setOpen(false); }} className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium ${view === id ? "bg-muni-celeste text-muni-navy" : "text-slate-200 hover:bg-white/10"}`}>
      <Icon className="h-4 w-4" aria-hidden="true" /> {label}
    </button>
  );
  const content = (
    <>
      <div className="mb-4 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <img src="/escudo-aguilares.png" alt="Escudo de Aguilares" className="h-10 w-auto" />
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muni-celeste">Cuidar</p>
            <p className="text-sm text-slate-300">Panel interno</p>
          </div>
        </div>
        <p className="mt-4 text-base font-semibold text-white">{user.full_name}</p>
        <p className="text-sm text-slate-300">{user.email} · {user.role}</p>
      </div>
      <nav className="space-y-1" aria-label="Panel">
        {item("cases", "Casos", LayoutDashboard)}
        {user.role === "admin" && item("users", "Usuarios", Users)}
      </nav>
      <button onClick={onLogout} className="mt-6 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-slate-200 hover:bg-white/10">
        <LogOut className="h-4 w-4" aria-hidden="true" /> Cerrar sesión
      </button>
    </>
  );
  return (
    <>
      <div className="flex items-center justify-between rounded-2xl bg-muni-navy p-4 text-white shadow-soft lg:hidden">
        <div className="flex min-w-0 items-center gap-3"><img src="/escudo-aguilares.png" alt="" className="h-9 w-auto" /><div className="min-w-0"><p className="truncate text-sm font-semibold">{user.full_name}</p><p className="truncate text-sm text-slate-300">{user.role}</p></div></div>
        <button className="rounded-lg p-2 text-white hover:bg-white/10" aria-label={open ? "Cerrar menú" : "Abrir menú"} onClick={() => setOpen((v) => !v)}>
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>
      {open && <div className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden" onClick={() => setOpen(false)} />}
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 bg-muni-navy p-4 shadow-xl transition-transform lg:static lg:z-auto lg:w-auto lg:translate-x-0 lg:rounded-2xl lg:shadow-soft ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-4 flex justify-end lg:hidden"><button className="rounded-lg p-2 text-slate-200 hover:bg-white/10" aria-label="Cerrar menú" onClick={() => setOpen(false)}><X className="h-5 w-5" /></button></div>
        {content}
      </aside>
    </>
  );
}
export type { PanelViewKey };
