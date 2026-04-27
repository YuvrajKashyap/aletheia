"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/search", label: "Search Lab" },
  { href: "/traces", label: "Query Traces" },
  { href: "/evaluations", label: "Evaluations" },
  { href: "/experiments", label: "Experiments" },
  { href: "/indexes", label: "Index Console" },
  { href: "/replay", label: "Replay Lab" },
  { href: "/datasets", label: "Datasets" }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden min-h-screen w-72 border-r border-slate-800 bg-slate-950/90 px-4 py-5 lg:block">
      <div className="px-2">
        <div className="text-lg font-semibold tracking-tight text-white">Aletheia</div>
        <div className="mt-1 text-xs leading-5 text-slate-400">
          Hybrid Retrieval, Reranking & Evaluation Platform
        </div>
      </div>
      <nav className="mt-8 space-y-1">
        {navItems.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block rounded-md px-3 py-2 text-sm transition focus:outline-none focus:ring-2 focus:ring-cyan-400/70",
                active
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
