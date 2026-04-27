import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "good" | "warn" | "bad";
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        tone === "neutral" && "border-slate-700 bg-slate-900 text-slate-300",
        tone === "good" && "border-emerald-800 bg-emerald-950 text-emerald-300",
        tone === "warn" && "border-amber-800 bg-amber-950 text-amber-300",
        tone === "bad" && "border-red-800 bg-red-950 text-red-300",
        className
      )}
      {...props}
    />
  );
}
