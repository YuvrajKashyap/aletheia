import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";

export function CorpusSearchControls({
  total,
  limit,
  offset,
  onLimitChange,
  onPrevious,
  onNext,
  children
}: {
  total?: number;
  limit: number;
  offset: number;
  onLimitChange: (limit: number) => void;
  onPrevious: () => void;
  onNext: () => void;
  children?: ReactNode;
}) {
  const end = Math.min(offset + limit, total ?? offset + limit);
  const hasPrevious = offset > 0;
  const hasNext = typeof total === "number" ? end < total : false;

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-3 md:flex-row md:items-center md:justify-between">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-xs text-slate-500">
          Page size
          <select
            className="ml-2 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-sm text-slate-100"
            value={limit}
            onChange={(event) => onLimitChange(Number(event.target.value))}
          >
            {[10, 25, 50, 100].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <span className="text-xs text-slate-500">
          {typeof total === "number"
            ? `${total ? offset + 1 : 0}-${end} of ${total}`
            : `offset ${offset}`}
        </span>
        {children}
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={onPrevious} disabled={!hasPrevious}>
          Previous
        </Button>
        <Button variant="secondary" onClick={onNext} disabled={!hasNext}>
          Next
        </Button>
      </div>
    </div>
  );
}
