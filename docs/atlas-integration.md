# Atlas Integration

Atlas is a separate planned project: a production-style distributed crawl, extract, index, and search platform for ethical public web content. It includes a URL frontier, robots.txt and politeness handling, Redis worker pipeline, Postgres storage, raw and cleaned content separation, extraction, dedupe, OpenSearch BM25 search, observability, freshness, recrawl logic, and a polished UI.

This integration is future-facing. It is not implemented in Aletheia today.

Related diagram:

- [Atlas Integration Flow](diagrams/atlas-integration-flow.md)

## Integration Model

Atlas crawls and cleans web documents. Aletheia can consume the resulting corpus as a retrieval, ranking, evaluation, and search observability layer.

Possible Aletheia dataset:

- dataset name: `atlas_web_v1`
- documents: crawled pages
- chunks: sections or paragraphs
- metadata: URL, domain, crawl timestamp, content hash, extraction method, language, and freshness fields

## Retrieval Over Atlas Data

Aletheia retrieval modes can apply to Atlas documents:

- BM25 for lexical web search
- dense retrieval for semantic matching
- hybrid RRF for combining lexical and semantic recall
- reranking for top-N candidate refinement

Query traces would help inspect which documents came from lexical retrieval, dense retrieval, fusion, and reranking.

## Evaluation Differences

SciFact includes qrels, so Aletheia can compute qrels-backed metrics directly.

Atlas web data would need a different evaluation strategy:

- human-labeled query sets
- editorial relevance judgments
- replay-based qualitative checks
- task-specific validation sets
- regression smoke checks over curated queries

Without qrels, Aletheia should not invent metrics.

## Hosting Strategy

The same cost-aware pattern applies:

- local full stack first
- public snapshot demos for real exported outputs
- optional hosted vector/search stack later

Atlas can generate fresh corpora. Aletheia can make ranking, replay, and evaluation behavior visible over those corpora.
