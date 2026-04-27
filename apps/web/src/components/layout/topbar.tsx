import { API_BASE_URL } from "@/lib/config";

export function Topbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 px-4 py-3 backdrop-blur md:px-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-100 lg:hidden">Aletheia</div>
          <div className="text-xs text-slate-500">Real API connection layer</div>
        </div>
        <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-400">
          API base: <span className="font-mono text-slate-200">{API_BASE_URL}</span>
        </div>
      </div>
    </header>
  );
}
