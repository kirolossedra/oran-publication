# M1-DR-04 — Keep full generated evidence local and publish a compact subset

- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** simulator sources, build products, model cache, logs, traces, animations and recovered payloads are large or generated.
- **Alternatives:** commit all run/build files; publish no data; commit small raw KPI/config files and keep full evidence locally.
- **Decision:** preserve all full build/run evidence under ignored simulator/ and commit only the effective YAML, raw upstream KPI JSON, SHA-256 list, and evidence note.
- **Reason:** keeps the repository reviewable while retaining complete local diagnostic evidence and a direct link between the published KPI/config and full local logs. Retrospective rationale based on repository storage policy and artifact sizes.
- **Consequences:** GitHub readers can inspect actual KPIs/config but cannot download the complete execution log or scheduler trace.
- **Disadvantages:** full remote evidence availability would require a separately approved artifact store or archival method.
- **Evidence:** [curated results](../../results/mission1-nr-baseline/README.md), [Mission 1 report](../missions/mission-1-installation.md), local hashes.
