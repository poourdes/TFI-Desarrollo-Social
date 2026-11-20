import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders base heading", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Cuidar" })).toBeInTheDocument();
  });
});
