# Evaluation

Aletheia evaluates retrieval with BEIR SciFact benchmark queries and relevance judgments. Evaluation correctness is backend-owned and uses real qrels.

## Dataset

Current SciFact counts:

- Documents: 5,183
- Benchmark queries: 300
- Relevance judgments: 339
- Chunks: 5,183 with the current document-level chunking strategy

SciFact qrels are document-level. Aletheia retrieves chunks, then maps retrieved chunks back to parent document IDs before scoring.

## Correctness Rules

Evaluation must:

- use real relevance judgments
- map chunk results to document IDs
- deduplicate document IDs before scoring
- avoid counting multiple chunks from the same document as multiple hits
- preserve query failures and partial run status
- store retrieval mode, index version, and configuration context

## Metrics

Aletheia stores and displays:

- Recall@5
- Recall@10
- MRR@10
- NDCG@10
- latency metrics including average, p50, and p95 where available

Latency values come from measured retrieval timings, not invented values.

## Evaluation Runner

The offline synchronous runner executes benchmark queries and stores:

- evaluation run metadata
- query-level results
- relevant document IDs
- retrieved document IDs
- trace IDs
- per-query metrics
- aggregate metrics
- JSON reports

Async evaluation jobs use Redis/RQ and the same backend-owned evaluation logic.

## Evaluation Reports

Evaluation reports are written as JSON under `reports/evaluations` and referenced from database rows. Reports are generated from real runs.

## Experiment Comparison

Experiment configs capture retrieval parameters. The Experiment Matrix groups evaluation runs by config, shows latest completed runs, and marks best-by-metric only when real comparable metrics exist.

## Golden Smoke

Golden smoke is a local-only qrels-backed regression sanity check. It uses conservative warn-mode thresholds by default and is not part of default GitHub CI.

It is useful before:

- major retrieval changes
- README metric updates
- public snapshot refreshes

Golden smoke thresholds are smoke checks, not final benchmark targets.

## Public Demo

The public demo shows real exported evaluation outputs from the local full stack. It does not run new public evaluation jobs.

## No Fake Metrics Policy

Aletheia does not invent benchmark values, qrels, latency values, or winners. Missing data is shown as missing.
