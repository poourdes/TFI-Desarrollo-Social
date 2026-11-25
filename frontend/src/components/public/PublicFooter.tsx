export function PublicFooter() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <p className="font-semibold text-slate-900">Cuidar</p>
            <p className="text-sm text-slate-600">Municipalidad de Aguilares · Oficina de Desarrollo Social</p>
            <p className="mt-2 text-sm text-slate-600">Aguilares, Tucumán, Argentina</p>
          </div>
          <div className="text-sm text-slate-600 sm:text-right">
            <p className="font-medium text-slate-800">Aviso de privacidad</p>
            <p className="mt-1">Las denuncias son anónimas por defecto. Los datos sensibles se cifran y solo accede personal autorizado.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
