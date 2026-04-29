# Replay Flow

This diagram shows saved query replay as trace-level debugging and regression support.

```mermaid
flowchart TD
  Saved[SavedQuery golden scifact] --> ReplayRequest[Replay request]
  ReplayRequest --> Mode[Chosen mode or config]
  Mode --> Search[Search service]
  Search --> Trace[QueryTrace]
  Trace --> Replay[QueryReplay]

  Qrels[Relevant docs from qrels] --> Compare[Replay comparison]
  Trace --> Compare
  Compare --> ComparisonJson[comparison_json]
  ComparisonJson --> Matched[Matched relevant docs]
  ComparisonJson --> Missed[Missed relevant docs]
  Replay --> ReplayUI[Replay Lab UI]
  ComparisonJson --> ReplayUI
```

## Notes

- Replay is trace-level debugging and regression support.
- Replay is not the same as a full evaluation run.
- Golden queries come from real SciFact qrels.
