import { SkeletonPage } from "@/components/layout/skeleton-page";

export default function SearchPage() {
  return (
    <SkeletonPage
      title="Search Lab"
      intent="Search Lab will run BM25, dense, hybrid, and rerank queries against the FastAPI search API."
    />
  );
}
