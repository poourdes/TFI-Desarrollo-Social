import { ArrowUpRight } from "lucide-react";

export function QuickExitButton() {
  return (
    <a
      href="https://www.google.com"
      className="fixed bottom-5 right-5 z-50 inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg hover:bg-slate-700 focus-visible:outline-brand-700"
      aria-label="Salida rápida a Google"
    >
      Salida rápida <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
    </a>
  );
}
