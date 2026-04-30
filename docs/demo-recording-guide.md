# Demo Recording Guide

## Recommended Length

- Recruiter walkthrough: 60 to 90 seconds.
- Technical walkthrough: 3 to 5 minutes.
- Avoid trying to cover every table row or every JSON field.

## Recording Setup

- Record at 1080p or better.
- Use a browser width around 1440 to 1600 px.
- Use browser zoom at 90% or 100%, whichever makes tables and cards cleaner.
- Use the public demo at https://aletheia.yuvrajkashyap.com unless intentionally recording local live mode.
- Keep tabs clean.
- Hide the bookmarks bar if it is distracting.
- Do not show local `.env` files, provider dashboards, terminal secrets, auth tokens, or private browser tabs.

## Route Order

1. `/`
2. `/search`
3. `/traces`
4. `/evaluations`
5. `/experiments`
6. `/indexes`
7. `/datasets`
8. `/replay`
9. `/system`
10. GitHub README

## Pre-Record Checklist

- Confirm `https://aletheia.yuvrajkashyap.com` loads.
- Confirm the public demo mode banner is visible.
- Confirm Search Lab has public demo scenarios.
- Confirm trace, evaluation, experiment, index, dataset, replay, and system pages load real snapshot data.
- Confirm no browser error page is visible.
- Confirm no private tabs, usernames, secrets, or local-only dashboards are visible.
- Have `docs/demo-walkthrough.md` open or printed for reference.

## Recording Checklist

- Start on the Overview page.
- State that public snapshot mode uses real exported outputs.
- Do not apologize for snapshot mode.
- Show Search Lab with a real scenario.
- Open or show a trace with retrieval stages and candidate provenance.
- Show evaluation and experiment comparison results.
- Show index metadata and dataset/qrels proof.
- Show Replay Lab and System Health.
- Close by explaining the full local stack and repo quality gates.

## Post-Record Checklist

- Watch the recording once before publishing.
- Confirm no secrets, private tabs, or account details are visible.
- Confirm the public demo is not described as live arbitrary hosted retrieval.
- Confirm benchmark and rerank claims match the README.
- Confirm audio is clear enough to understand technical terms.
- Export in a practical size for hosting.

## Filename Conventions

- `aletheia-90s-demo.mp4`
- `aletheia-technical-walkthrough.mp4`
- `aletheia-readme-demo.gif`

Use GIF only if it is small and useful. Prefer MP4 for a complete walkthrough.

## Storage

If a small video or GIF is committed later, place it under:

```text
docs/assets/video/
```

For larger videos, prefer external hosting:

- YouTube unlisted
- Loom
- Personal site
- GitHub release asset

Do not commit large video files unless the repository size impact is intentional.
