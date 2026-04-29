# Evaluation Flow

This diagram shows qrels-backed evaluation from benchmark query to stored report.

```mermaid
flowchart TD
  BQ[BenchmarkQuery] --> Search[Search service]
  Search --> Chunks[Retrieved chunks]
  Chunks --> ParentDocs[Map chunks to documents]
  ParentDocs --> Dedup[Deduplicate document IDs]

  Qrels[Relevance judgments] --> Metrics[Metrics engine]
  Dedup --> Metrics

  Metrics --> Run[EvaluationRun]
  Metrics --> QueryResult[EvaluationQueryResult]
  Metrics --> Report[EvaluationReport JSON]
  Search --> Trace[QueryTrace]
  Trace --> QueryResult
```

## Notes

- Metrics are document-level because SciFact qrels are document-level.
- Qrels are not invented.
- Zero metric values are valid when retrieval misses relevant documents.
