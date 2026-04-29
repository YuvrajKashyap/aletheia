# Retrieval Design

Aletheia implements four retrieval modes over the same corpus and index metadata: BM25, dense, hybrid reciprocal rank fusion, and hybrid plus reranking. The goal is inspectable retrieval behavior, not answer generation.

## Corpus Units

SciFact records are stored as documents and chunks. The current SciFact chunking strategy is document-level, so each document corresponds to one chunk. This keeps evaluation alignment straightforward because SciFact qrels are document-level.

For larger or longer corpora, chunking can move to paragraph or section granularity, but evaluation still needs to map chunk hits back to parent documents before scoring.

## BM25 Retrieval

BM25 retrieval is handled by OpenSearch.

Strengths:

- strong lexical matching
- transparent term-based behavior
- good exact-match baseline
- useful for scientific terminology and identifiers

Weaknesses:

- misses semantic matches with different wording
- depends on tokenization and query wording
- does not use embedding similarity

## Dense Retrieval

Dense retrieval uses `BAAI/bge-small-en-v1.5` embeddings and Qdrant vector similarity.

Strengths:

- captures semantic similarity
- can retrieve relevant passages without exact lexical overlap
- complements BM25 for paraphrased queries

Weaknesses:

- local model inference has latency
- semantic matches can be less transparent
- vector quality depends on the embedding model and corpus domain

## Hybrid Retrieval

Hybrid retrieval combines BM25 and dense candidate lists with Reciprocal Rank Fusion.

Aletheia uses RRF because raw BM25 scores and dense vector scores are not directly comparable. RRF combines rank positions rather than trying to normalize unrelated score scales.

The default `rrf_k` is `60`.

## Cross-Encoder Reranking

Hybrid rerank first retrieves a candidate set, then reranks only the top-N candidates with `cross-encoder/ms-marco-MiniLM-L-6-v2`.

Reranking only top-N is intentional:

- cross-encoder scoring is more expensive than retrieval
- reranking too many candidates increases latency
- the reranker is most useful after recall-oriented candidate generation

This creates a quality and latency tradeoff that Aletheia exposes through traces, metrics, and experiment comparisons.

## Retrieval Modes

- `bm25`: OpenSearch BM25 only
- `dense`: Qdrant dense retrieval only
- `hybrid`: BM25 plus dense candidates fused with RRF
- `hybrid_rerank`: hybrid retrieval followed by cross-encoder reranking

## Trace Fields

Trace and candidate records expose stage-specific ranking information where available:

- BM25 rank and score
- dense rank and score
- fusion rank and score
- rerank rank and score
- final rank
- retrieval source
- latency fields

These fields support debugging retrieval behavior without turning the system into a chatbot.

## Limitations

- SciFact is a small benchmark corpus.
- Local CPU model inference can add latency.
- Public snapshot mode is precomputed and read-only.
- Public snapshot mode does not run arbitrary live retrieval.
- Metrics should be interpreted as qrels-backed evaluation outputs, not broad production guarantees.
