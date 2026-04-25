# AGENTS.md



## Purpose



This file defines the rules for all future AI agents, Codex sessions, and implementation assistants working on Aletheia.



Aletheia is a production-style hybrid retrieval, reranking, evaluation, and search observability platform. It must preserve its identity as a serious retrieval infrastructure project.



Execution agents must follow the assigned step only. Do not expand the scope. Do not skip ahead. Do not build unrelated features.



This project is managed by a main architect chat. Execution agents should complete only the assigned step, report clearly, and then stop.



## Project identity



Aletheia is:



\- A hybrid retrieval platform

\- A reranking platform

\- An evaluation platform

\- A search observability platform

\- A production-style portfolio project using real benchmark data



Aletheia is not:



\- A chatbot

\- A generic RAG wrapper

\- A fake analytics dashboard

\- A vector database toy demo

\- A notebook-only project

\- A frontend-only project

\- An OpenAI API wrapper

\- A hardcoded search demo



Always preserve the retrieval, ranking, evaluation, and observability identity of this project.



## Locked stack



Do not change the stack unless the project owner explicitly instructs you to do so.



### Frontend



\- Next.js

\- TypeScript

\- Tailwind CSS

\- shadcn/ui

\- Recharts



### Backend



\- Python

\- FastAPI

\- Pydantic

\- SQLAlchemy

\- Alembic



### Database



\- PostgreSQL

\- Docker Postgres for local development

\- Neon Postgres for hosted database



### Queue and worker



\- Redis

\- RQ



### Retrieval infrastructure



\- OpenSearch for BM25 lexical retrieval

\- Qdrant for dense vector retrieval



### Models



\- BAAI/bge-small-en-v1.5 for embeddings

\- cross-encoder/ms-marco-MiniLM-L-6-v2 for reranking



### Dataset



\- BEIR SciFact



### Testing



\- pytest



### Local development



\- Docker Compose



## Non-negotiable architecture rule



FastAPI owns all backend logic.



Correct pattern:



\- Frontend calls FastAPI.

\- FastAPI uses SQLAlchemy to access PostgreSQL.

\- FastAPI talks to OpenSearch.

\- FastAPI talks to Qdrant.

\- FastAPI talks to Redis and RQ.

\- Workers execute background jobs through backend-owned logic.



Incorrect pattern:



\- Frontend talks directly to PostgreSQL.

\- Frontend uses Supabase client to access database tables directly.

\- Frontend talks directly to OpenSearch.

\- Frontend talks directly to Qdrant.

\- Frontend owns backend business logic.

\- Frontend computes official evaluation metrics by itself.



Do not bypass FastAPI.



Do not make the frontend talk directly to the database.



Do not use Supabase-specific backend magic for this project. If hosted Postgres is needed, use Neon.



## Data truth rules



Do not fake data.



Do not create placeholder metrics and present them as real.



Do not hardcode evaluation results.



Do not invent latency numbers.



Do not fake query traces.



Do not fake index status.



Do not fake system health.



Do not create dashboards that look complete while the backend is not actually producing the data.



Temporary mock data is allowed only if the assigned step explicitly asks for it, and it must be clearly labeled as temporary development mock data. Mock data must never be treated as final demo data.



The final demo must use:



\- Real SciFact corpus data

\- Real SciFact queries

\- Real SciFact qrels

\- Real OpenSearch BM25 retrieval

\- Real Qdrant dense retrieval

\- Real hybrid RRF results

\- Real reranker output

\- Real evaluation metrics

\- Real query traces

\- Real latency measurements



## Evaluation correctness rules



Evaluation correctness is more important than visual polish.



Agents must preserve these rules:



\- Evaluation must use real relevance judgments.

\- Chunk-level retrieval results must map back to document IDs before scoring.

\- Document-level deduplication must happen before metrics are computed.

\- Multiple chunks from the same document must not count as multiple document hits.

\- Metrics must be computed from stored retrieval results or actual evaluation runs.

\- Recall@5, Recall@10, MRR@10, and NDCG@10 must be implemented carefully.

\- p50 and p95 latency must come from measured timings.

\- Failed or partial evaluation runs must be visibly marked.

\- Retrieval mode, index version, reranker setting, and run timestamp must be stored for evaluation context.



Do not optimize away correctness to make the UI look finished faster.



## Retrieval mode rules



Aletheia must support and preserve these retrieval modes:



1\. BM25

2\. Dense

3\. Hybrid RRF

4\. Hybrid plus reranker



Do not remove these modes.



Do not collapse the project into one generic search mode.



Do not replace retrieval with a chatbot answer.



Do not replace retrieval with a single OpenAI API call.



## Indexing rules



Indexes must be treated as versioned system assets.



Rules:



\- Indexes must have versions.

\- Indexes must have statuses.

\- Failed indexes must never auto-activate.

\- Active index changes must be explicit.

\- Index build jobs should be idempotent where practical.

\- Index build jobs should be retry-safe where practical.

\- Index state should be visible through the backend.

\- The UI must not claim an index is active unless the backend confirms it.



## Job and worker rules



Background jobs should be production-style.



Rules:



\- Use Redis and RQ for worker-backed jobs.

\- Jobs should have IDs.

\- Jobs should expose status.

\- Jobs should be retry-safe where practical.

\- Jobs should avoid duplicate destructive work.

\- Long-running work should not block normal API request handling.

\- Worker heartbeat should be added later.

\- System events should be added later.



## API rules



The API should be versioned under:



\- /api/v1



General rules:



\- Use FastAPI.

\- Use Pydantic schemas for request and response validation.

\- Use SQLAlchemy for database access.

\- Use Alembic for migrations.

\- Use structured errors.

\- Include request IDs, trace IDs, and job IDs where relevant.

\- All list endpoints should eventually support pagination and filtering.

\- Expensive or administrative endpoints must later be protected by ADMIN\_API\_KEY.

\- Do not expose secrets.

\- Do not expose internal admin actions publicly.



## Frontend rules



The frontend is a dashboard and control surface for the retrieval platform.



It should include these final pages:



1\. Search Lab

2\. Query Trace

3\. Evaluation Dashboard

4\. Experiment Comparison

5\. Index Console

6\. Document Explorer

7\. System Health



Frontend rules:



\- Use real backend data for final demo pages.

\- Do not make fake metrics look real.

\- Do not compute official backend-owned metrics only in the browser.

\- Do not bypass FastAPI.

\- Keep the UI serious, technical, and polished.

\- Favor clarity over visual noise.

\- Show empty, loading, error, and failed states honestly.

\- Show timestamps and run metadata where useful.

\- Make it clear when data comes from a completed real run.



## Security and demo safety rules



Public demo safety matters.



Rules:



\- Public demo users may explore real results.

\- Public demo users must not be able to trigger expensive admin actions.

\- Ingestion, reindexing, index activation, and expensive evaluation jobs must later be protected.

\- ADMIN\_API\_KEY or equivalent protection must be added before exposing admin actions.

\- Demo mode may restrict write actions.

\- Demo mode must not fake system state.

\- Production mode must not expose secrets or internal-only controls.



## Development process rules



Do not skip architecture.



Do not jump ahead.



Do not create extra folders, services, or dependencies unless the assigned step asks for them.



Do not install packages unless the assigned step asks for package installation.



Do not create Docker Compose unless the assigned step asks for Docker Compose.



Do not create FastAPI code unless the assigned step asks for backend code.



Do not create Next.js code unless the assigned step asks for frontend code.



Do not create database models unless the assigned step asks for models.



Do not add paid API dependencies for core retrieval.



Do not change the project direction because a simpler demo would be easier.



Always stop at the requested step.



## Reporting rules



Every execution agent must report back in this fixed format:



Step completed:

Files created:

Files modified:

Commands run:

Validation result:

Issues or concerns:

Return to the main architect chat for the next step.



## File change explanation rule



Whenever files are created or modified, explain:



\- What changed

\- Why it changed

\- How to validate it



Do not just say "done."



## Validation command rule



Every implementation step must include validation commands.



Examples may include:



\- dir

\- dir docs

\- git status

\- pytest

\- backend test commands

\- frontend build commands

\- lint commands

\- migration commands

\- Docker health checks



Use validation commands appropriate to the assigned step.



## Windows 11 rule



The setup must remain Windows 11 friendly.



When giving local commands, prefer PowerShell-compatible commands unless the user explicitly requests another shell.



Avoid assuming a Unix-only environment.



## Final instruction



Aletheia must remain a real retrieval, reranking, evaluation, and observability platform.



Do not turn it into a chatbot.



Do not turn it into a RAG wrapper.



Do not turn it into a fake dashboard.



Do not proceed beyond the assigned step.


