import type { ReactNode } from "react";

import { DemoModeBanner } from "@/components/demo/demo-mode-banner";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="lg:flex">
        <Sidebar />
        <div className="min-w-0 flex-1">
          <Topbar />
          <DemoModeBanner />
          <main className="mx-auto max-w-7xl px-4 py-6 md:px-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
