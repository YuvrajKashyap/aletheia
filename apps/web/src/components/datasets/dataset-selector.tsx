import type { DatasetSummary } from "@/lib/api/types";

export function DatasetSelector({
  datasets,
  selectedDatasetId,
  onChange
}: {
  datasets: DatasetSummary[];
  selectedDatasetId: string | null;
  onChange: (datasetId: string) => void;
}) {
  return (
    <label className="block text-sm text-slate-400">
      Dataset
      <select
        className="mt-2 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/70 md:w-80"
        value={selectedDatasetId ?? ""}
        onChange={(event) => onChange(event.target.value)}
      >
        {datasets.map((dataset) => (
          <option key={dataset.id} value={dataset.id}>
            {dataset.name} {dataset.version}
          </option>
        ))}
      </select>
    </label>
  );
}
