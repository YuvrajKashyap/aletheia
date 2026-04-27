import { cn } from "@/lib/utils";

export type DatasetTab = "documents" | "chunks" | "queries" | "qrels";

const tabs: { id: DatasetTab; label: string }[] = [
  { id: "documents", label: "Documents" },
  { id: "chunks", label: "Chunks" },
  { id: "queries", label: "Benchmark Queries" },
  { id: "qrels", label: "Relevance Judgments" }
];

export function DatasetTabs({
  activeTab,
  onChange
}: {
  activeTab: DatasetTab;
  onChange: (tab: DatasetTab) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-slate-800">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={cn(
            "border-b-2 px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70",
            activeTab === tab.id
              ? "border-cyan-300 text-cyan-200"
              : "border-transparent text-slate-400 hover:text-slate-100"
          )}
          onClick={() => onChange(tab.id)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
