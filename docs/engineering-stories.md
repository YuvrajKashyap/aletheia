# Engineering Stories

These stories are concise interview prompts for explaining implementation and debugging work without overstating incident severity.

## 1. One Active Index Version Invariant

Symptom: Index activation could become ambiguous if more than one version looked active or if activation state was not handled transactionally.

Root cause: Index versions need a clear invariant: the system should know which version is active, and failed or partial builds should not become active by accident.

Fix: Tightened the activation flow so active index changes are explicit and the UI reflects backend-confirmed state.

Lesson: Versioned assets need lifecycle rules, not just rows in a table.

Production thinking: Search systems need safe promotion and rollback semantics because index state affects every query.

## 2. Limited Index Build Metadata Corruption Bug

Symptom: A limited index build risked making corpus-level metadata look like the full corpus had fewer documents or chunks than it actually had.

Root cause: Limited builds are useful for testing, but their counts must not overwrite full corpus metadata.

Fix: Kept limited build metadata scoped to the build while preserving corpus-level counts.

Lesson: Test and partial workflows must not corrupt global truth.

Production thinking: Operational shortcuts need guardrails so local validation does not damage system metadata.

## 3. `trace_json.trace_id` Null Bug

Symptom: Trace JSON could omit or null out the trace identifier, which made deep links and trace debugging less reliable.

Root cause: The persisted trace row and serialized trace JSON had to stay aligned.

Fix: Ensured trace identifiers were included consistently in the trace payload and UI links.

Lesson: Observability data is only useful when identifiers are stable across storage, API responses, and UI links.

Production thinking: Traceability depends on durable IDs and consistent propagation.

## 4. Search Lab Stale Error State

Symptom: Search Lab could keep showing an old error after a later successful search or state transition.

Root cause: UI error state was not cleared cleanly when a new request or snapshot scenario succeeded.

Fix: Updated state handling so loading, success, empty, and error states do not contradict each other.

Lesson: Retrieval UI needs honest state transitions, especially when backend availability varies.

Production thinking: Stale errors reduce trust in operational dashboards.

## 5. Vercel Framework Mis-Detection

Symptom: The public frontend deployment required Vercel to treat `apps/web` as the Next.js project root.

Root cause: Monorepo-style layouts can confuse automatic framework detection if project root and build settings are not explicit.

Fix: Documented and configured the frontend deployment path and build settings.

Lesson: Deployment readiness includes platform configuration, not just code that builds locally.

Production thinking: Build settings should be reproducible and documented.

## 6. Snapshot Data Loading On Vercel

Symptom: Static snapshot JSON files were reachable directly in the browser, but the Overview initially showed unavailable snapshot files in production.

Root cause: Server-side loading behavior differed from browser-side public static file access on Vercel.

Fix: Moved Overview snapshot loading to a client-side path that fetches `/demo-data/*.json` directly.

Lesson: Static asset availability and server runtime fetch behavior are not always equivalent.

Production thinking: Hosted runtime behavior needs direct validation, not just local assumptions.

## 7. Recharts Container Warnings

Symptom: Chart components could warn when rendered in containers without stable dimensions.

Root cause: Responsive chart libraries need predictable parent sizing.

Fix: Adjusted chart/container usage so dashboard charts render with stable layout expectations.

Lesson: Data visualization polish depends on layout constraints as much as chart configuration.

Production thinking: UI warnings often point to reliability and readability problems.

## 8. Redis/RQ Worker Heartbeat And Job Observability

Symptom: Background jobs need visible state so the UI can distinguish queued work, running work, failures, and worker availability.

Root cause: Long-running ingestion, indexing, evaluation, comparison, and replay jobs should not be opaque.

Fix: Added worker heartbeat and system health surfaces around job execution and backend state.

Lesson: Async systems need operational visibility, not just enqueue calls.

Production thinking: Users and operators need to know whether work is delayed, failed, or waiting for a worker.
