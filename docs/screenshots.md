# Screenshot Guide

Screenshots are not committed yet. This guide lists the final capture plan so future README and demo assets use real UI states and real exported data.

Store final image files under:

```text
docs/assets/screenshots/
```

## Capture Plan

| Filename | Route/source | Mode | What to show | Notes |
| --- | --- | --- | --- | --- |
| overview-public-snapshot.png | `/` | Public snapshot | Overview with snapshot banner and exported counts | Use the public demo after final visual QA. |
| search-lab-hybrid-rerank.png | `/search` | Public snapshot or local live | Search Lab scenario with result cards and trace link | Use a real exported scenario. |
| trace-rerank-detail.png | `/traces` | Public snapshot or local live | Candidate table, stages, and rank movement | Do not fabricate trace data. |
| evaluations-dashboard.png | `/evaluations` | Public snapshot | Metrics cards and query result table | Use an exported evaluation run. |
| experiment-matrix.png | `/experiments` | Public snapshot | Config matrix and best-by-metric indicators | Admin disabled state may be visible if it helps explain snapshot mode. |
| index-console.png | `/indexes` | Public snapshot | Active index metadata and local-only admin copy | Do not imply live hosted OpenSearch or Qdrant health. |
| dataset-browser.png | `/datasets` | Public snapshot | Dataset stats and sample rows | Make sample-data scope clear. |
| replay-lab.png | `/replay` | Public snapshot | Replay details and matched or missed docs | Use a real exported replay. |
| system-health-snapshot.png | `/system` | Public snapshot | Honest snapshot and local-only service state | No fake backend health. |
| github-actions-ci.png | GitHub Actions | GitHub | Passing Aletheia CI run | Use the real CI page. |
| vercel-public-demo.png | Public demo | Public snapshot | Hosted Vercel demo with snapshot banner | Use https://aletheia.yuvrajkashyap.com. |

## Policy

- Do not add fake screenshots.
- Do not create placeholder PNG, JPG, or WebP files.
- Capture screenshots only after final visual QA.
- Screenshots must show real public snapshot data or real local live outputs.
- If a UI state requires a local full-stack run, capture it locally and label it as local live mode in surrounding documentation.
