import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function SkeletonPage({
  title,
  intent
}: {
  title: string;
  intent: string;
}) {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <Badge tone="neutral">Next build step</Badge>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{intent}</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Implementation coming in the next build step</CardTitle>
            <CardDescription>
              This page is intentionally a route foundation only. It does not include fake data,
              placeholder charts, or invented metrics.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400">
              Backend-owned data and workflows will be connected here when this section is implemented.
            </p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
