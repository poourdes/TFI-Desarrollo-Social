import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const areasResponse = {
  notice: "Esta plataforma no es para emergencias.",
  emergency_lines: [{ numero: "911", etiqueta: "Emergencias generales" }],
  captcha: { provider: "mock", site_key: null },
  areas: [
    {
      id: "b5b9f4c9-4d1e-5f1a-9c2e-6f4e8b1a2d76",
      nombre: "Adultos mayores",
      slug: "adultos-mayores",
      descripcion: null,
      anonymity: "standard",
      form: {
        situation_types: [{ value: "neglect", label: "Negligencia" }],
        relationship_options: [],
        fields: [
          {
            key: "situation_type",
            label: "Tipo de situación",
            required: true,
            choices: null,
          },
          {
            key: "description",
            label: "Relato de los hechos",
            required: true,
            choices: null,
          },
        ],
      },
    },
  ],
};

function mockFetch() {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/areas")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => areasResponse,
      });
    }
    if (url.endsWith("/api/reports/adultos-mayores") && init?.method === "POST") {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => ({
          tracking_code: "CUID-2ABC-3DEF-4GHI",
          case_number: "CASO-202611-0001",
          area_slug: "adultos-mayores",
          status: "received",
          created_at: "2026-11-24T12:00:00Z",
        }),
      });
    }
    return Promise.reject(new Error(`Unexpected request: ${url}`));
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("App", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders base heading", async () => {
    mockFetch();
    render(<App />);
    expect(screen.getByRole("heading", { name: "Cuidar" })).toBeInTheDocument();
    await screen.findByText("Adultos mayores");
  });

  it("submits the public form to the area-scoped endpoint", async () => {
    const fetchMock = mockFetch();
    render(<App />);

    expect(await screen.findByText("Adultos mayores")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Área"), {
      target: { value: "adultos-mayores" },
    });
    fireEvent.change(screen.getByLabelText("Tipo de situación *"), {
      target: { value: "neglect" },
    });
    fireEvent.change(screen.getByLabelText("Relato de los hechos *"), {
      target: { value: "Una denuncia de prueba con longitud suficiente." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Enviar denuncia" }));

    await waitFor(() =>
      expect(screen.getByText(/CUID-2ABC-3DEF-4GHI/)).toBeInTheDocument(),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/reports/adultos-mayores"),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });
});
