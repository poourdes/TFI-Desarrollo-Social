import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  confirmEscalation, getPanelCase, getPanelCases, login, logout, recordVisit, revealContact, transitionCase,
  type AuthenticatedUser, type CaseDetail, type PanelCase,
} from "../../api";
import { CaseDetailView } from "./CaseDetailView";
import { CasesTable } from "./CasesTable";
import { PanelSidebar, type PanelViewKey } from "./PanelSidebar";
import { SummaryCards } from "./SummaryCards";

function messageOf(e: unknown) { return e instanceof Error ? e.message : "Error inesperado"; }

export function PanelPage({ onGoPublic }: { onGoPublic: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [cases, setCases] = useState<PanelCase[]>([]);
  const [status, setStatus] = useState("");
  const [query, setQuery] = useState("");
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [details, setDetails] = useState<Record<string, CaseDetail | undefined>>({});
  const [notes, setNotes] = useState("");
  const [contacts, setContacts] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [view, setView] = useState<PanelViewKey>("cases");

  async function loadCases(nextStatus = status) {
    const list = await getPanelCases(nextStatus || undefined);
    setCases(list);
    const entries = await Promise.all(list.slice(0, 20).map(async (c) => [c.id, await getPanelCase(c.id)] as const).map((p) => p.catch(() => null)));
    setDetails((d) => { const n = { ...d }; for (const e of entries) if (e) n[e[0]] = e[1]; return n; });
  }

  useEffect(() => { if (user) void loadCases(); }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    try { const u = await login(email, password); setUser(u); setError(""); }
    catch (err) { setError(messageOf(err)); }
  }
  async function openCase(id: string) { const d = await getPanelCase(id); setDetail(d); setDetails((m) => ({ ...m, [id]: d })); setNotes(""); }
  async function apply(action: Promise<CaseDetail>) { const d = await action; setDetail(d); setDetails((m) => ({ ...m, [d.id]: d })); setCases(await getPanelCases(status || undefined)); }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return cases.filter((c) => !q || c.case_number.toLowerCase().includes(q) || c.area_name.toLowerCase().includes(q));
  }, [cases, query]);

  if (!user) {
    return (
      <div className="min-h-screen bg-sand-50 px-4 py-12">
        <div className="mx-auto max-w-md rounded-3xl bg-white p-6 shadow-soft ring-1 ring-slate-100 sm:p-8">
          <button onClick={onGoPublic} className="text-sm font-medium text-brand-700 hover:text-brand-800">← Volver al sitio público</button>
          <h1 className="mt-4 text-2xl font-semibold text-slate-900">Ingreso al panel</h1>
          <p className="mt-1 text-sm text-slate-600">Acceso para personal autorizado.</p>
          <form className="mt-6 space-y-4" onSubmit={handleLogin}>
            <div><label className="block text-sm font-medium text-slate-700" htmlFor="email">Email</label><input id="email" type="email" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
            <div><label className="block text-sm font-medium text-slate-700" htmlFor="password">Contraseña</label><input id="password" type="password" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5" value={password} onChange={(e) => setPassword(e.target.value)} required /></div>
            <button className="w-full rounded-xl bg-brand-700 px-4 py-2.5 font-semibold text-white hover:bg-brand-800" type="submit">Ingresar</button>
          </form>
          {error && <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sand-50 text-slate-900">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[260px_1fr] sm:px-6">
        <PanelSidebar user={user} view={view} onView={setView} onLogout={() => { void logout().finally(() => { setUser(null); setDetail(null); onGoPublic(); }); }} />
        <main className="space-y-6">
          <div>
            <h1 className="text-2xl font-semibold">Panel de casos</h1>
            <p className="text-sm text-slate-600">Gestión interna de denuncias y seguimiento.</p>
          </div>
          {view === "users" ? (
            <div className="rounded-2xl bg-white p-6 shadow-soft ring-1 ring-slate-100"><h2 className="font-semibold">Usuarios</h2><p className="mt-2 text-sm text-slate-600">La gestión de usuarios está disponible mediante el endpoint de administración.</p></div>
          ) : (
            <>
              <SummaryCards cases={cases} details={details} />
              <div className="flex flex-col gap-3 rounded-2xl bg-white p-4 shadow-soft ring-1 ring-slate-100 sm:flex-row sm:items-center">
                <label className="sr-only" htmlFor="case-search">Buscar caso</label>
                <input id="case-search" placeholder="Buscar por caso o área" className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm sm:max-w-xs" value={query} onChange={(e) => setQuery(e.target.value)} />
                <label className="sr-only" htmlFor="status-filter">Filtrar por estado</label>
                <select id="status-filter" aria-label="Filtrar por estado" className="rounded-xl border border-slate-300 px-3 py-2 text-sm" value={status} onChange={(e) => { setStatus(e.target.value); void loadCases(e.target.value); }}>
                  <option value="">Todos los estados</option><option value="open">Abierto</option><option value="in_review">En revisión</option><option value="closed">Cerrado</option>
                </select>
              </div>
              <CasesTable cases={filtered} onOpen={(id) => void openCase(id)} />
              {detail && <CaseDetailView detail={detail} notes={notes} setNotes={setNotes} onTransition={(t) => void apply(transitionCase(detail.id, t))} onVisit={() => void apply(recordVisit(detail.id, notes))} onConfirm={() => void apply(confirmEscalation(detail.id))} onReveal={(id) => void revealContact(id).then((r) => setContacts((c) => ({ ...c, [id]: r.contact })))} contacts={contacts} />}
            </>
          )}
          {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}
        </main>
      </div>
    </div>
  );
}
