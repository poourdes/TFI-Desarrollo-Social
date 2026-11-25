import { useEffect, useRef, useState, type FormEvent } from "react";
import { submitReport, type PublicArea, type PublicAreasResponse, type ReportCreated, type ReportPayload } from "../../api";
import { AreaCards } from "./AreaCards";
import { ConfirmationScreen } from "./ConfirmationScreen";

declare global {
  interface Window {
    turnstile?: {
      render: (el: HTMLElement, opts: { sitekey: string; callback: (t: string) => void }) => string;
      reset: (id?: string) => void;
    };
  }
}

const steps = ["Área", "Qué pasó", "Dónde y cuándo", "Contacto opcional", "Confirmar"];
function choicesFor(area: PublicArea, key: string) {
  if (key === "situation_type") return area.form.situation_types;
  if (key === "relationship_to_victim") return area.form.relationship_options;
  return area.form.fields.find((f) => f.key === key)?.choices ?? [];
}
function fieldVisible(area: PublicArea | null, key: string) {
  return !!area?.form.fields.some((f) => f.key === key);
}

export function ReportStepper({ data }: { data: PublicAreasResponse | null }) {
  const [step, setStep] = useState(0);
  const [slug, setSlug] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [wantContact, setWantContact] = useState(false);
  const [created, setCreated] = useState<ReportCreated | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [captchaToken, setCaptchaToken] = useState("");
  const captchaRef = useRef<HTMLDivElement | null>(null);
  const widgetId = useRef<string | null>(null);

  const area = data?.areas.find((a) => a.slug === slug) ?? null;

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
    if (document.getElementById(scriptId)) { renderWidget(); return; }
    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    script.async = true; script.defer = true; script.onload = renderWidget;
    document.body.appendChild(script);
  }, [data]);

  function reset() {
    setStep(0); setSlug(""); setValues({}); setWantContact(false); setCreated(null); setError(""); setCaptchaToken("");
    if (window.turnstile && widgetId.current) window.turnstile.reset(widgetId.current);
  }
  function setField(key: string, value: string) { setValues((v) => ({ ...v, [key]: value })); }

  function validateCurrent(): string | null {
    if (!area) return "Seleccioná un área.";
    const requiredVisible = (keys: string[]) =>
      keys.filter((k) => fieldVisible(area, k)).filter((k) => area.form.fields.find((f) => f.key === k)?.required);
    if (step === 0 && !slug) return "Seleccioná un área para continuar.";
    if (step === 1) for (const k of requiredVisible(["situation_type", "description"])) if (!values[k]?.trim()) return `Completá el campo requerido.`;
    if (step === 2) for (const k of requiredVisible(["locality", "address", "incident_date", "affected_name", "affected_initials", "age_range", "relationship_to_victim"])) if (!values[k]?.trim()) return "Completá los campos requeridos de este paso.";
    if (step === 3 && wantContact && fieldVisible(area, "contact") && !values.contact?.trim()) return "Ingresá un contacto o desactivá la opción.";
    return null;
  }

  function next() { const v = validateCurrent(); if (v) { setError(v); return; } setError(""); setStep((s) => Math.min(s + 1, steps.length - 1)); }
  function back() { setError(""); setStep((s) => Math.max(s - 1, 0)); }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!area) return;
    const v = validateCurrent(); if (v) { setError(v); return; }
    const payload: ReportPayload = {};
    for (const field of area.form.fields) {
      if (field.key === "contact" && !wantContact) continue;
      const value = values[field.key]?.trim();
      if (value) payload[field.key] = value;
    }
    if (data?.captcha.provider === "turnstile") payload.captcha_token = captchaToken;
    setSubmitting(true);
    try {
      setCreated(await submitReport(area.slug, payload));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setSubmitting(false);
    }
  }

  if (created) return <ConfirmationScreen created={created} onNew={reset} />;

  const renderField = (key: string) => {
    if (!area || !fieldVisible(area, key)) return null;
    const field = area.form.fields.find((f) => f.key === key);
    if (!field) return null;
    const choices = choicesFor(area, key);
    const id = `field-${key}`;
    const label = <label className="block text-sm font-medium text-slate-700" htmlFor={id}>{field.label}{field.required ? " *" : ""}</label>;
    const cls = "mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 shadow-sm";
    return <div key={key}>{label}{choices.length > 0 ? (
      <select id={id} className={cls} required={field.required} value={values[key] ?? ""} onChange={(e) => setField(key, e.target.value)}>
        <option value="">Seleccione</option>
        {choices.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
      </select>
    ) : key === "description" ? (
      <textarea id={id} className={`${cls} min-h-32`} required={field.required} value={values[key] ?? ""} onChange={(e) => setField(key, e.target.value)} />
    ) : (
      <input id={id} type={key === "incident_date" ? "date" : "text"} className={cls} required={field.required} value={values[key] ?? ""} onChange={(e) => setField(key, e.target.value)} />
    )}</div>;
  };

  return (
    <div className="rounded-3xl bg-white p-5 shadow-soft ring-1 ring-slate-100 sm:p-8">
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>Paso {step + 1} de {steps.length}</span><span>{steps[step]}</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-slate-100">
          <div className="h-2 rounded-full bg-brand-600 transition-all" style={{ width: `${((step + 1) / steps.length) * 100}%` }} />
        </div>
        <div className="mt-3 hidden gap-2 text-xs sm:flex">{steps.map((s, i) => <span key={s} className={`rounded-full px-2 py-1 ${i <= step ? "bg-brand-50 text-brand-800" : "bg-slate-100 text-slate-500"}`}>{s}</span>)}</div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {step === 0 && (
          <div>
            <p className="mb-3 text-sm font-medium text-slate-700">Seleccioná el área relacionada con la situación.</p>
            <AreaCards areas={data?.areas ?? []} selected={slug} onSelect={(s) => { setSlug(s); setValues({}); setError(""); }} />
            <div className="sr-only">
              <label htmlFor="area">Área</label>
              <select id="area" value={slug} onChange={(e) => { setSlug(e.target.value); setValues({}); }}>
                <option value="">Seleccione un ǭrea</option>
                {(data?.areas ?? []).map((a) => <option key={a.id} value={a.slug}>{a.nombre}</option>)}
              </select>
            </div>
          </div>
        )}
        {step === 1 && <div className="space-y-4">{renderField("situation_type")}{renderField("description")}</div>}
        {step === 2 && <div className="space-y-4">{["affected_name","affected_initials","age_range","relationship_to_victim","locality","address","incident_date"].map(renderField)}</div>}
        {step === 3 && (
          <div className="space-y-4">
            <div className="rounded-2xl bg-sand-50 p-4 ring-1 ring-slate-200">
              <label className="flex items-start gap-3">
                <input type="checkbox" className="mt-1 h-4 w-4 rounded border-slate-300 text-brand-700" checked={wantContact} onChange={(e) => setWantContact(e.target.checked)} />
                <div>
                  <span className="font-medium text-slate-900">Quiero que me contacten</span>
                  <p className="text-sm text-slate-600">Opcional. Si no lo activás, la denuncia se envía de forma anónima.</p>
                </div>
              </label>
            </div>
            {wantContact && fieldVisible(area, "contact") && renderField("contact")}
          </div>
        )}
        {step === 4 && (
          <div className="space-y-4">
            <div className="rounded-2xl bg-sand-50 p-5 ring-1 ring-slate-200">
              <h3 className="font-semibold text-slate-900">Revisá tu denuncia</h3>
              <dl className="mt-3 space-y-2 text-sm text-slate-700">
                <div><dt className="font-medium text-slate-500">Área</dt><dd>{area?.nombre}</dd></div>
                {area?.form.fields.filter((f) => values[f.key]?.trim() && (f.key !== "contact" || wantContact)).map((f) => (
                  <div key={f.key}><dt className="font-medium text-slate-500">{f.label}</dt><dd className="whitespace-pre-wrap">{choicesFor(area, f.key).find((c) => c.value === values[f.key])?.label ?? values[f.key]}</dd></div>
                ))}
              </dl>
            </div>
            {data?.captcha.provider === "turnstile" && <div ref={captchaRef} />}
          </div>
        )}

        {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
          <button type="button" onClick={back} disabled={step === 0} className="rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-40">Atrás</button>
          {step < steps.length - 1 ? (
            <button type="button" onClick={next} className="rounded-xl bg-brand-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-800">Continuar</button>
          ) : (
            <button type="submit" disabled={submitting} className="rounded-xl bg-brand-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-800 disabled:opacity-60">{submitting ? "Enviando..." : "Enviar denuncia"}</button>
          )}
        </div>
      </form>
    </div>
  );
}
