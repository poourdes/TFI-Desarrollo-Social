import { ArrowUpRight } from "lucide-react";

export function QuickExitButton() {
  return (
    <a
      href="https://www.google.com"
      className="fixed bottom-4 right-4 z-50 inline-flex items-center gap-2 rounded-full bg-muni-navy px-4 py-3 text-sm font-semibold text-white shadow-lg hover:bg-slate-800 focus-visible:outline-muni-celeste sm:bottom-5 sm:right-5"
      aria-label="Salida rápida a Google"
    >
      Salida rápida <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
    </a>
  );
}
