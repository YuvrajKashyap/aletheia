import { progressPercent } from "@/components/indexes/index-format";

type IndexProgressBarProps = {
  completed?: number | null;
  total?: number | null;
};

export function IndexProgressBar({ completed, total }: IndexProgressBarProps) {
  const percent = progressPercent(completed, total);
  if (percent === null) {
    return <span className="text-slate-500">Unavailable</span>;
  }

  return (
    <div className="min-w-36">
      <div className="h-2 overflow-hidden rounded-full bg-slate-900">
        <div className="h-full rounded-full bg-cyan-300" style={{ width: `${percent}%` }} />
      </div>
      <div className="mt-1 font-mono text-xs text-slate-400">{percent.toFixed(1)}%</div>
    </div>
  );
}
