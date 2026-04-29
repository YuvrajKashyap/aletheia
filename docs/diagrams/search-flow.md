# Search Flow

This diagram shows the four retrieval modes and the records produced for observability.

```mermaid
flowchart TD
  Query[Search query] --> QueryRow[Query row]
  Query --> Mode{Retrieval mode}

  Mode --> BM25Mode[BM25]
  BM25Mode --> OS[OpenSearch]
  OS --> BM25Candidates[BM25 candidates]

  Mode --> DenseMode[Dense]
  DenseMode --> Emb[Embedding model]
  Emb --> QD[Qdrant]
  QD --> DenseCandidates[Dense candidates]

  Mode --> HybridMode[Hybrid]
  HybridMode --> BM25Candidates
  HybridMode --> DenseCandidates
  BM25Candidates --> RRF[Reciprocal Rank Fusion]
  DenseCandidates --> RRF
  RRF --> HybridRank[Final hybrid rank]

  Mode --> RerankMode[Hybrid rerank]
  RerankMode --> RRF
  RRF --> TopN[Hybrid top N]
  TopN --> Reranker[Cross encoder reranker]
  Reranker --> RerankRank[Final rerank rank]

  BM25Candidates --> CandidateRows[RetrievalCandidate rows]
  DenseCandidates --> CandidateRows
  HybridRank --> CandidateRows
  RerankRank --> CandidateRows

  CandidateRows --> Trace[QueryTrace row]
  Trace --> SlowEvent[SystemEvent slow query warning]
```

## Notes

- RRF uses rank positions, not raw score mixing.
- The reranker only scores top-N candidates.
- Aletheia does not generate answers and does not provide chatbot behavior.
