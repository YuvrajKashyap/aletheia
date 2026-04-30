# Project Closeout

This is the final completion record for Aletheia as a resume, GitHub, and public demo project.

## Final Status

- Aletheia is complete as a resume/GitHub/public demo project.
- Public demo is live in snapshot mode.
- Full local live stack is documented and reproducible.
- CI is expected green through the local and GitHub quality gates.
- Resume, recruiter, portfolio, and interview materials exist.
- No fake data policy remains in force.

## Final Links

- Public demo: https://aletheia.yuvrajkashyap.com
- GitHub repo: https://github.com/YuvrajKashyap/aletheia
- README: `README.md`
- Docs index: `docs/docs-index.md`
- Screenshots: `docs/screenshots.md`
- Resume copy: `docs/final-resume-copy.md`
- Interview package: `docs/interview-package.md`

## What Is Built

- FastAPI backend.
- Next.js frontend.
- PostgreSQL metadata store.
- Redis/RQ async job system.
- OpenSearch BM25 retrieval.
- Qdrant dense vector retrieval.
- Local embedding model: `BAAI/bge-small-en-v1.5`.
- Local reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Docker-based local full stack.
- Public Vercel snapshot demo.
- Evaluation and benchmark system.
- Experiment comparison matrix.
- Saved query and golden query replay harness.
- Query tracing and search observability.
- Index console and system health views.
- CI, docs, screenshots, diagrams, runbooks, and audit tooling.

## What Is Intentionally Not Hosted Live

The public demo does not host:

- OpenSearch.
- Qdrant.
- Redis/RQ.
- Worker processes.
- Live arbitrary search.
- Reranker/model serving.
- Admin jobs such as indexing, evaluation, comparison, and replay execution.

This is a cost-aware and honest architecture decision. The public demo uses real exported outputs from the full local pipeline. It is not fake, and it does not pretend to be a publicly hosted live search cluster.

## Final Benchmark Summary

| Mode | Scope | Queries | Failed | Recall@5 | Recall@10 | MRR@10 | NDCG@10 | Avg ms | P95 ms | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| bm25 | Full | 300 | 0 | 0.7187 | 0.7707 | 0.6296 | 0.6574 | 54.8 | 84.2 | Full 300-query SciFact benchmark. |
| dense | Full | 300 | 0 | 0.7624 | 0.8386 | 0.6705 | 0.7077 | 1144.5 | 1057.6 | Full 300-query SciFact benchmark using BAAI/bge-small-en-v1.5. |
| hybrid | Full | 300 | 0 | 0.7558 | 0.8429 | 0.6698 | 0.7055 | 856.6 | 949.8 | Full 300-query SciFact benchmark using Reciprocal Rank Fusion. |
| hybrid_rerank | Sampled | 50 | 0 | 0.7633 | 0.7933 | 0.6733 | 0.6969 | 3265.9 | 3399.4 | Sampled rerank benchmark. Not directly comparable to full 300-query runs. |

These metrics are real generated benchmark outputs. The `hybrid_rerank` row is sampled and is not directly comparable to the full 300-query rows.

## Final Caveats

- Public demo is snapshot-backed.
- Full live stack currently runs locally.
- Public demo does not run live arbitrary retrieval.
- Hybrid rerank benchmark is sampled.
- Atlas integration is future-facing and not implemented in this repo.
- There is no production users claim.
- Local CPU model latency is higher than optimized hosted inference would be.

## What To Use On Resume

Use `docs/final-resume-copy.md`.

## What To Say In Interviews

Start with:

- `docs/interview-package.md`
- `docs/interview-q-and-a.md`
- `docs/system-design-walkthrough.md`
- `docs/engineering-stories.md`

## Future Optional Work

- Record a short demo video.
- Host a full live backend if budget allows.
- Integrate Atlas as a future corpus source.
- Add larger benchmark datasets.
- Add auth and admin roles.
- Optimize model serving and latency.
