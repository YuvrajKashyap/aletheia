import { Suspense } from "react";

import { TraceBrowser } from "@/components/traces/trace-browser";

export default function TracesPage() {
  return (
    <Suspense fallback={null}>
      <TraceBrowser />
    </Suspense>
  );
}
