export function PublicFooter() {
  return (
    <footer className="bg-muni-navy text-white">
      <div className="mx-auto w-full max-w-6xl px-4 py-10 pb-24 sm:px-6 sm:pb-10 lg:px-8 2xl:max-w-7xl">
        <div className="grid gap-8 sm:grid-cols-2 sm:items-start">
          <div className="flex items-start gap-3">
            <img src="/escudo-aguilares.png" alt="Escudo de Aguilares" className="h-12 w-auto" />
            <div>
              <p className="text-base font-semibold">Cuidar</p>
              <p className="text-sm text-slate-200 sm:text-base">Municipalidad de Aguilares · Oficina de Desarrollo Social</p>
              <p className="mt-2 text-sm text-slate-300">Aguilares, Tucumán, Argentina</p>
            </div>
          </div>
          <div className="text-sm text-slate-200 sm:text-right sm:text-base">
            <p className="font-medium text-white">Aviso de privacidad</p>
            <p className="mt-1">Las denuncias son anónimas por defecto. Los datos sensibles se cifran y solo accede personal autorizado.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
