# Public Snapshot Architecture

This diagram shows how the public demo serves real exported data without hosting the full live search stack.

```mermaid
flowchart TD
  Recruiter[Recruiter browser] --> Vercel[Vercel Next.js frontend]
  Vercel --> DemoData["/demo-data static JSON"]
  DemoData --> Pages[Snapshot UI pages]

  Local[Local full stack] --> ExportScript[export-demo-snapshot.ps1]
  ExportScript --> ExportCli[export_demo_snapshot.py]
  ExportCli --> JsonFiles[apps web public demo-data JSON]
  JsonFiles --> GitHub[GitHub repo]
  GitHub --> Vercel

  Neon[Neon Postgres schema] -. schema only .-> Vercel
  LiveBackend[Live FastAPI backend] -. not hosted publicly .-> Vercel
  SearchStack[OpenSearch Qdrant Redis worker models] -. not hosted publicly .-> Vercel
```

## Notes

- The public demo uses real exported outputs.
- Live retrieval and admin jobs are disabled publicly.
- This is a cost-aware architecture, not fake data.
- The public demo does not run live arbitrary search.
