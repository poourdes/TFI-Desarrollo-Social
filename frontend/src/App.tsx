import { useState } from "react";
import { PanelPage } from "./components/panel/PanelPage";
import { PublicPage } from "./components/public/PublicPage";

export default function App() {
  const [view, setView] = useState<"public" | "panel">("public");
  if (view === "public") return <PublicPage onGoPanel={() => setView("panel")} />;
  return <PanelPage onGoPublic={() => setView("public")} />;
}
