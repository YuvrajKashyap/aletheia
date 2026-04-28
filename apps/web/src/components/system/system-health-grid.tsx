import { ServiceHealthCard } from "@/components/system/service-health-card";
import type { OperationalStatus } from "@/components/system/operational-status-badge";
import { workerOperationalStatus, workerTimestamp } from "@/components/system/worker-status";
import type {
  DbHealthResponse,
  HealthResponse,
  ModelStatusResponse,
  OpenSearchHealthResponse,
  QdrantHealthResponse,
  QueueStatusResponse,
  WorkerHeartbeatItem
} from "@/lib/api/types";

type Result<T> = {
  data: T | null;
  error: string | null;
};

function statusFromHealth(status?: string, error?: string | null): OperationalStatus {
  if (error) return "error";
  if (status === "ok" || status === "healthy") return "healthy";
  if (status === "unhealthy" || status === "error") return "error";
  return status ? "warning" : "unknown";
}

function modelStatus(model: ModelStatusResponse | null, error: string | null): OperationalStatus {
  if (error || model?.error) return "error";
  if (model?.loaded) return "healthy";
  if (model) return "warning";
  return "unknown";
}

function latestWorker(workers: WorkerHeartbeatItem[]): WorkerHeartbeatItem | null {
  return workers[0] || null;
}

export function SystemHealthGrid({
  api,
  db,
  queue,
  workers,
  openSearch,
  qdrant,
  embedding,
  reranker
}: {
  api: Result<HealthResponse>;
  db: Result<DbHealthResponse>;
  queue: Result<QueueStatusResponse>;
  workers: Result<WorkerHeartbeatItem[]>;
  openSearch: Result<OpenSearchHealthResponse>;
  qdrant: Result<QdrantHealthResponse>;
  embedding: Result<ModelStatusResponse>;
  reranker: Result<ModelStatusResponse>;
}) {
  const worker = latestWorker(workers.data || []);
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <ServiceHealthCard
        title="API"
        description="FastAPI application health."
        status={statusFromHealth(api.data?.status, api.error)}
        error={api.error}
        fields={[
          { label: "Service", value: api.data?.service },
          { label: "Version", value: api.data?.version },
          { label: "App mode", value: api.data?.app_mode },
          { label: "Request ID", value: api.data?.request_id, mono: true }
        ]}
      />
      <ServiceHealthCard
        title="Postgres"
        description="Database connectivity check."
        status={statusFromHealth(db.data?.status, db.error || db.data?.error)}
        error={db.error || db.data?.error}
        fields={[
          { label: "Status", value: db.data?.status },
          { label: "Database", value: db.data?.database },
          { label: "Request ID", value: db.data?.request_id, mono: true }
        ]}
      />
      <ServiceHealthCard
        title="Redis Queue"
        description="RQ queue reachability."
        status={queue.error ? "error" : queue.data ? "healthy" : "unknown"}
        error={queue.error || queue.data?.error}
        fields={[
          { label: "Queue", value: queue.data?.queue },
          { label: "Job count", value: queue.data?.job_count },
          { label: "Status", value: queue.data?.status || (queue.data ? "reachable" : undefined) }
        ]}
      />
      <ServiceHealthCard
        title="Worker"
        description="Latest worker heartbeat."
        status={workerOperationalStatus(worker, workers.error)}
        error={workers.error}
        fields={[
          { label: "Worker", value: worker?.worker_name },
          { label: "Queue", value: worker?.queue_name },
          { label: "Status", value: worker?.status || (workers.data ? "No recent worker heartbeat" : undefined) },
          { label: "Current job", value: worker?.current_job_id, mono: true },
          { label: "Last seen", value: worker ? workerTimestamp(worker) : undefined }
        ]}
      />
      <ServiceHealthCard
        title="OpenSearch"
        description="BM25 lexical retrieval backend."
        status={statusFromHealth(openSearch.data?.status, openSearch.error || openSearch.data?.error)}
        error={openSearch.error || openSearch.data?.error}
        fields={[
          { label: "URL", value: openSearch.data?.url },
          { label: "Cluster", value: openSearch.data?.cluster_name },
          { label: "Version", value: openSearch.data?.version }
        ]}
      />
      <ServiceHealthCard
        title="Qdrant"
        description="Dense vector retrieval backend."
        status={statusFromHealth(qdrant.data?.status, qdrant.error || qdrant.data?.error)}
        error={qdrant.error || qdrant.data?.error}
        fields={[
          { label: "URL", value: qdrant.data?.url },
          { label: "Version", value: qdrant.data?.version },
          { label: "Collections", value: qdrant.data?.collections_count }
        ]}
      />
      <ServiceHealthCard
        title="Embedding model"
        description="Dense retrieval embedding model."
        status={modelStatus(embedding.data, embedding.error)}
        error={embedding.error || embedding.data?.error}
        fields={[
          { label: "Model", value: embedding.data?.model_name },
          { label: "Loaded", value: embedding.data?.loaded },
          { label: "Device", value: embedding.data?.device },
          { label: "Dimension", value: embedding.data?.embedding_dimension },
          { label: "Cache", value: embedding.data?.cache_dir, mono: true }
        ]}
      />
      <ServiceHealthCard
        title="Reranker model"
        description="Hybrid rerank cross-encoder."
        status={modelStatus(reranker.data, reranker.error)}
        error={reranker.error || reranker.data?.error}
        fields={[
          { label: "Model", value: reranker.data?.model_name },
          { label: "Loaded", value: reranker.data?.loaded },
          { label: "Device", value: reranker.data?.device },
          { label: "Cache", value: reranker.data?.cache_dir, mono: true }
        ]}
      />
    </div>
  );
}
