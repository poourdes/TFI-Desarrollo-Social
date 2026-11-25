import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  confirmEscalation,
  getPanelCase,
  getPanelCases,
  getPublicAreas,
  login,
  recordVisit,
  revealContact,
  submitReport,
  transitionCase,
  type AuthenticatedUser,
  type CaseDetail,
  type PanelCase,
  type PublicArea,
  type PublicAreasResponse,
  type ReportCreated,
  type ReportPayload,
} from "./api";

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : "Error inesperado";
}

function choicesFor(area: PublicArea, key: string) {
  if (key === "situation_type") return area.form.situation_types;
  if (key === "relationship_to_victim") return area.form.relationship_options;
  return area.form.fields.find((field) => field.key === key)?.choices ?? [];
}

declare global {
  interface Window {
    turnstile?: {
      render: (
        element: HTMLElement,
        options: { sitekey: string; callback: (token: string) => void },
      ) => string;
      reset: (widgetId?: string) => void;
    };
  }
}

function PublicReportForm() {
  const [data, setData] = useState<PublicAreasResponse | null>(null);
  const [slug, setSlug] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [created, setCreated] = useState<ReportCreated | null>(null);
  const [error, setError] = useState("");
  const [captchaToken, setCaptchaToken] = useState("");
  const captchaRef = useRef<HTMLDivElement | null>(null);
  const widgetId = useRef<string | null>(null);

  useEffect(() => {
    void getPublicAreas()
      .then(setData)
      .catch((reason: unknown) => setError(messageOf(reason)));
  }, []);

  useEffect(() => {
    if (data?.captcha.provider !== "turnstile" || !data.captcha.site_key) return;
    const scriptId = "turnstile-script";
    const renderWidget = () => {
      if (!captchaRef.current || !window.turnstile || widgetId.current) return;
      widgetId.current = window.turnstile.render(captchaRef.current, {
        sitekey: data.captcha.site_key as string,
        callback: (token: string) => setCaptchaToken(token),
      });
    };
    if (document.getElementById(scriptId)) {
      renderWidget();
      return;
    }
    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    script.async = true;
    script.defer = true;
    script.onload = renderWidget;
    document.body.appendChild(script);
  }, [data]);

  const area = data?.areas.find((candidate) => candidate.slug === slug) ?? null;

  function selectArea(nextSlug: string) {
    setSlug(nextSlug);
    setValues({});
    setCreated(null);
    setError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (area === null) return;
    const payload: ReportPayload = {};
    for (const field of area.form.fields) {
      const value = values[field.key]?.trim();
      if (value) payload[field.key] = value;
    }
    if (data?.captcha.provider === "turnstile") {
      payload.captcha_token = captchaToken;
    }
    try {
      setCreated(await submitReport(area.slug, payload));
      setError("");
      if (window.turnstile && widgetId.current) window.turnstile.reset(widgetId.current);
      setCaptchaToken("");
    } catch (reason: unknown) {
      setError(messageOf(reason));
    }
  }

  return (
    <section className="rounded-lg bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">Nueva denuncia</h2>
      {data !== null && <p className="mt-2 text-sm text-slate-600">{data.notice}</p>}
      <label className="mt-4 block text-sm font-medium" htmlFor="area">
        Área
      </label>
      <select
        id="area"
        className="mt-1 w-full rounded border border-slate-300 p-2"
        value={slug}
        onChange={(event) => selectArea(event.target.value)}
      >
        <option value="">Seleccione un área</option>
        {data?.areas.map((candidate) => (
          <option key={candidate.id} value={candidate.slug}>
            {candidate.nombre}
          </option>
        ))}
      </select>

      {area !== null && (
        <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
          {area.form.fields.map((field) => {
            const choices = choicesFor(area, field.key);
            return (
              <div key={field.key}>
                <label
                  className="block text-sm font-medium"
                  htmlFor={`field-${field.key}`}
                >
                  {field.label}
                  {field.required ? " *" : ""}
                </label>
                {choices.length > 0 ? (
                  <select
                    id={`field-${field.key}`}
                    className="mt-1 w-full rounded border border-slate-300 p-2"
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(event) =>
                      setValues({
                        ...values,
                        [field.key]: event.target.value,
                      })
                    }
                  >
                    <option value="">Seleccione</option>
                    {choices.map((choice) => (
                      <option key={choice.value} value={choice.value}>
                        {choice.label}
                      </option>
                    ))}
                  </select>
                ) : field.key === "description" ? (
                  <textarea
                    id={`field-${field.key}`}
                    className="mt-1 w-full rounded border border-slate-300 p-2"
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(event) =>
                      setValues({
                        ...values,
                        [field.key]: event.target.value,
                      })
                    }
                  />
                ) : (
                  <input
                    id={`field-${field.key}`}
                    type={field.key === "incident_date" ? "date" : "text"}
                    className="mt-1 w-full rounded border border-slate-300 p-2"
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(event) =>
                      setValues({
                        ...values,
                        [field.key]: event.target.value,
                      })
                    }
                  />
                )}
              </div>
            );
          })}
          {data?.captcha.provider === "turnstile" && <div ref={captchaRef} />}
          <button className="rounded bg-slate-800 px-4 py-2 text-white" type="submit">
            Enviar denuncia
          </button>
        </form>
      )}
      {created !== null && (
        <div className="mt-4 rounded bg-emerald-50 p-4 text-sm">
          <p>Caso: {created.case_number}</p>
          <p>
            Código de seguimiento (guárdelo, no se volverá a mostrar):{" "}
            <strong>{created.tracking_code}</strong>
          </p>
        </div>
      )}
      {error !== "" && <p className="mt-4 text-sm text-red-700">{error}</p>}
      {data?.emergency_lines.map((line) => (
        <p key={line.numero} className="mt-2 text-xs text-slate-600">
          {line.etiqueta}: {line.numero}
        </p>
      ))}
    </section>
  );
}

function PanelView() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [cases, setCases] = useState<PanelCase[]>([]);
  const [status, setStatus] = useState("");
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [notes, setNotes] = useState("");
  const [contacts, setContacts] = useState<Record<string, string>>({});
  const [error, setError] = useState("");

  async function loadCases(nextStatus = status) {
    setCases(await getPanelCases(nextStatus || undefined));
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const authenticated = await login(email, password);
      setUser(authenticated);
      await loadCases("");
      setError("");
    } catch (reason: unknown) {
      setError(messageOf(reason));
    }
  }

  async function openCase(caseId: string) {
    setDetail(await getPanelCase(caseId));
    setNotes("");
  }

  async function applyDetail(action: Promise<CaseDetail>) {
    setDetail(await action);
    setError("");
  }

  async function handleContact(reportId: string) {
    try {
      const result = await revealContact(reportId);
      setContacts({ ...contacts, [reportId]: result.contact });
    } catch (reason: unknown) {
      setError(messageOf(reason));
    }
  }

  if (user === null) {
    return (
      <section className="rounded-lg bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Ingreso al panel</h2>
        <form className="mt-4 space-y-3" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-medium" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="mt-1 w-full rounded border border-slate-300 p-2"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium" htmlFor="password">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              className="mt-1 w-full rounded border border-slate-300 p-2"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          <button className="rounded bg-slate-800 px-4 py-2 text-white" type="submit">
            Ingresar
          </button>
        </form>
        {error !== "" && <p className="mt-4 text-sm text-red-700">{error}</p>}
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="rounded-lg bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Panel de casos</h2>
        <p className="mt-1 text-sm text-slate-600">
          {user.full_name} — {user.email}
        </p>
        <div className="mt-4 flex gap-2">
          <select
            aria-label="Filtrar por estado"
            className="rounded border border-slate-300 p-2"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              void loadCases(event.target.value);
            }}
          >
            <option value="">Todos los estados</option>
            <option value="open">Abierto</option>
            <option value="in_review">En revisión</option>
            <option value="closed">Cerrado</option>
          </select>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg bg-white p-4 shadow-sm">
          <h3 className="font-semibold">Casos visibles</h3>
          <ul className="mt-2 space-y-2">
            {cases.map((item) => (
              <li key={item.id}>
                <button
                  className="w-full rounded border border-slate-200 p-2 text-left text-sm hover:bg-slate-50"
                  onClick={() => void openCase(item.id)}
                >
                  {item.case_number} — {item.area_name} — {item.status}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-lg bg-white p-4 shadow-sm">
          {detail === null ? (
            <p className="text-sm text-slate-600">Seleccione un caso.</p>
          ) : (
            <>
              <h3 className="font-semibold">{detail.case_number}</h3>
              <p className="text-sm text-slate-600">
                {detail.area_name} — {detail.status}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {detail.allowed_transitions.map((target) => (
                  <button
                    key={target}
                    className="rounded border border-slate-300 px-2 py-1 text-xs"
                    onClick={() => void applyDetail(transitionCase(detail.id, target))}
                  >
                    Pasar a {target}
                  </button>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <input
                  aria-label="Notas de la visita"
                  className="flex-1 rounded border border-slate-300 p-2 text-sm"
                  placeholder="Notas de la visita"
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                />
                <button
                  className="rounded bg-slate-800 px-3 py-2 text-xs text-white"
                  onClick={() => void applyDetail(recordVisit(detail.id, notes))}
                >
                  Registrar visita
                </button>
              </div>
              {detail.pending_escalation && (
                <button
                  className="mt-3 rounded bg-amber-600 px-3 py-2 text-xs text-white"
                  onClick={() => void applyDetail(confirmEscalation(detail.id))}
                >
                  Confirmar escalamiento sugerido
                </button>
              )}
              <ul className="mt-4 space-y-3">
                {detail.reports.map((report) => (
                  <li key={report.id} className="border-t border-slate-200 pt-2">
                    <p className="text-sm">{report.description}</p>
                    {report.has_contact && (
                      <button
                        className="text-xs text-blue-700 underline"
                        onClick={() => void handleContact(report.id)}
                      >
                        Ver contacto
                      </button>
                    )}
                    {contacts[report.id] !== undefined && (
                      <p className="text-xs">{contacts[report.id]}</p>
                    )}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
      {error !== "" && <p className="text-sm text-red-700">{error}</p>}
    </section>
  );
}

export default function App() {
  const [view, setView] = useState<"public" | "panel">("public");

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-4xl px-6 py-16">
        <header className="mb-8 flex items-end justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-600">
              Municipalidad de Aguilares
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Cuidar</h1>
          </div>
          <div className="flex gap-2 text-sm">
            <button
              className={view === "public" ? "font-semibold" : "text-slate-600"}
              onClick={() => setView("public")}
            >
              Denunciar
            </button>
            <button
              className={view === "panel" ? "font-semibold" : "text-slate-600"}
              onClick={() => setView("panel")}
            >
              Panel
            </button>
          </div>
        </header>
        {view === "public" ? <PublicReportForm /> : <PanelView />}
      </div>
    </main>
  );
}
