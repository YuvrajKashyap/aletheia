import { SkeletonPage } from "@/components/layout/skeleton-page";

export default function ExperimentsPage() {
  return (
    <SkeletonPage
      title="Experiments"
      intent="Experiments will manage retrieval configs and compare real evaluation runs across BM25, dense, hybrid, and rerank modes."
    />
  );
}
