const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface Choice {
  value: string;
  label: string;
}

export interface PublicFormField {
  key: string;
  label: string;
  required: boolean;
  choices: Choice[] | null;
}

export interface PublicArea {
  id: string;
  nombre: string;
  slug: string;
  descripcion: string | null;
  anonymity: string;
  form: {
    situation_types: Choice[];
    relationship_options: Choice[];
    fields: PublicFormField[];
  };
}

export interface PublicAreasResponse {
  notice: string;
  emergency_lines: Array<{ numero: string; etiqueta: string }>;
  captcha: { provider: string; site_key: string | null };
  areas: PublicArea[];
}

export interface ReportPayload {
  [key: string]: string | undefined;
  captcha_token?: string;
}

export interface ReportCreated {
  tracking_code: string;
  case_number: string;
  area_slug: string;
  status: string;
  created_at: string;
}

export interface AuthenticatedUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  areas: Array<{ id: string; slug: string; nombre: string }>;
}

export interface PanelCase {
  id: string;
  case_number: string;
  area_slug: string;
  area_name: string;
  status: string;
  report_count: number;
  created_at: string;
}

export interface PanelReport {
  id: string;
  situation_type: string;
  locality: string;
  address: string | null;
  description: string;
  status: string;
  incident_date: string | null;
  created_at: string;
  has_contact: boolean;
}

export interface CaseDetail extends PanelCase {
  allowed_transitions: string[];
  pending_escalation: boolean;
  reports: PanelReport[];
  timeline: Array<{ event_type: string; message: string; created_at: string }>;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let detail = `Error ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      throw new Error(detail);
    }
    throw new Error(detail);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function getPublicAreas(): Promise<PublicAreasResponse> {
  return request<PublicAreasResponse>("/api/areas");
}

export function submitReport(
  areaSlug: string,
  payload: ReportPayload,
): Promise<ReportCreated> {
  return request<ReportCreated>(`/api/reports/${areaSlug}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(email: string, password: string): Promise<AuthenticatedUser> {
  return request<AuthenticatedUser>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getPanelCases(status?: string): Promise<PanelCase[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<PanelCase[]>(`/api/panel/cases${query}`);
}

export function getPanelCase(caseId: string): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/panel/cases/${caseId}`);
}

export function transitionCase(caseId: string, target: string): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/panel/cases/${caseId}/transition`, {
    method: "POST",
    body: JSON.stringify({ target }),
  });
}

export function recordVisit(caseId: string, notes: string): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/panel/cases/${caseId}/visit`, {
    method: "POST",
    body: JSON.stringify({ notes: notes || null }),
  });
}

export function confirmEscalation(caseId: string): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/panel/cases/${caseId}/escalation/confirm`, {
    method: "POST",
    body: JSON.stringify({ confirm: true }),
  });
}

export function revealContact(reportId: string): Promise<{ contact: string }> {
  return request<{ contact: string }>(`/api/panel/reports/${reportId}/contact`);
}
