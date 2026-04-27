import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "secondary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-9 items-center justify-center rounded-md px-3 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70 disabled:pointer-events-none disabled:opacity-50",
        variant === "primary" && "bg-cyan-300 text-slate-950 hover:bg-cyan-200",
        variant === "secondary" && "border border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800",
        variant === "ghost" && "text-slate-300 hover:bg-slate-900 hover:text-white",
        className
      )}
      {...props}
    />
  );
}
