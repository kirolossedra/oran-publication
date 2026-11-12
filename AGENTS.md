# Research governance

This repository prepares a separate O-RAN/5G RAN resource-allocation study. The human researcher owns research questions, hypotheses, priorities, and scientific interpretation. Work only within this project unless specifically authorized. Do not reuse or link the historical NR-U simulator tree or its compiler patches.

## Mandatory sanity gate before expensive experiments

**Scientific leadership workflow:** The PI defines the research gap, questions, and acceptable scientific interpretations. Codex is responsible for execution, debugging, and delivering verifiable measurements, not proposing repeated large campaigns to discover simple implementation bugs. Do not ask the PI to manually run fragmented commands when a reproducible entrypoint can execute them. Implement and test fixes in one integrated iteration, documenting substantive decisions without creating a new mission or approval gate for every small debug step.

The versioned working package is `campaigns/20261111-g1-integrated-v2/`. Its `source-overrides/model/` files must be reconciled with the separate **local** `simulator/ns-3.48/contrib/iboran/model/` source files; GitHub changes do not update the WSL simulator automatically. Never modify a simulator source tree while an experiment process using it is active. Before syncing overrides, inspect discrepancies, stop any active experiment at a safe boundary, and preserve all uncommitted local source changes. The sanity command explicitly backs up mismatched local files when `--apply-overrides` is provided. Do not overwrite unreviewed local work.

**Codex's required single command on the provisioned WSL device (from repo root):**

```bash
bash campaigns/20261111-g1-integrated-v2/scripts/sanity_g1.sh --apply-overrides
```

The active execution handoff is [issue #25](https://github.com/kirolossedra/oran-publication/issues/25) ([Codex] G1 high-throughput sanity). When Codex runs this task, document the actual WSL execution command, simulator compilation status, success/failure counts, UL/DL throughput, and starvation verdict there. Merely reading this file or opening the issue does not launch any simulation.

The command validates checksums, saves original differing files, runs focused Python regression tests, rebuilds `ns3iboran_nr` (default `-j 2`), runs a **20-cell diagnostic subset** with `tqdm` progress, invokes the canonical campaign analyzer, and emits a human-readable sanity report and machine-readable CSV/JSON. The 20 cases are the first matched seed: both LOS interventions × both policies × four loads at stationary mobility (16), plus both interventions × both policies under high bidirectional contention with controlled mobility (4). Each case measures **both DL and UL**. This does **not** replace the 160-cell/5-seed campaign and is not publication-grade inference. The runner also uses `tqdm` to show progress in the full campaign; install `tqdm` in the pinned Python environment if unavailable (it has a plain-text fallback).

**High-throughput KPI gate — never omit throughput.** For every scenario, direction, and UE, retain:
- Configured offered load (Mbps), *measured* application TX throughput (Mbps), received application goodput (Mbps), and MAC-reported actual/achievable rate (Mbps). Show six-UE aggregates, per-UE values, and goodput fairness (Jain index); distinguish Mbps from MB/s.
- TX/RX packet counts, PDR, lost/unreceived-at-stop, duplication/reordering, P50/P95/P99 one-way application latency and its sample count. Latency measures received packets; no reception means an **undefined** percentile, not 0 ms. Do not call application end-to-end delay pure RAN latency; label modeled backhaul.
- Actual applied MAC grant counts, PRB-symbol totals/shares, MCS, reported CQI and CQI-input observability, queue occupancy and bytes, time to first grant, and longest observed backlogged interval without a grant. Do not substitute planned allocations for applied DCI grants.
- Applied channel condition and UE position/motion audit. Compare matched all-LOS to selective UE6-NLOS rather than treating arbitrary baseline UE disparities as causal effects.

The sanity outputs are in distinct timestamped paths under `simulator/runs/20261111-g1-integrated-v2-sanity/` and `results/20261111-g1-integrated-v2-sanity/`, including `sanity-summary.md`, `sanity-throughput-by-scenario.csv`, `sanity-per-ue.csv`, `sanity-starvation.csv`, `sanity-verdict.json`, and all canonical analyzer tables. Raw experiments are append-only. Do not pool original policy results with the modified scheduler implementations. The diagnostic flags **RoundRobin** if any UE has at least 1 second of continuously observed positive backlog without an actual grant. **TopKCqi with k=1 remains greedy and may starve UEs even when correctly implemented**; report that separately and investigate CQI/grant path, do not silently impose fairness or describe it as a proven bug. The 1-second threshold is an engineering alarm, not a standards threshold.

**If sanity fails:** Codex must inspect the exact failing raw traces and logs, fix the underlying code, rebuild and rerun **sanity only** with a new timestamped result directory, and present before/after evidence. Do not proceed to 160 runs while sanity is failing. If sanity passes, present concrete UL/DL throughput and starvation evidence to the PI and wait for research-level approval before expensive new campaign execution. Report only observations actually reproduced in WSL; do not claim that merely committing a GitHub script proves the simulator executes successfully.

## Mission lifecycle and documentation gate

Every mission must begin with a report based on `templates/MISSION-TEMPLATE.md`, documenting its objective, scope, rationale, requirements, and acceptance criteria. Identify existing architecture/components, risks, dependencies, and verification evidence before implementation. Explain important alternatives and decisions, distinguishing recorded reasons from retrospective inference.

Document every source/configuration change, its purpose and effect, dependencies and versions, effective parameters, commands, seeds, statistical methods, results, failures, troubleshooting, limitations, and unresolved questions. Preserve full logs and immutable raw outputs under unique run-specific locations. Do not overwrite earlier data. Include GitHub-compatible Mermaid diagrams for architecture, topology, data flow, algorithms, or workflow changes; explain and label conceptual diagrams.

Classify claims as source-verified, observed, interpretation, hypothesis, planned, or unverified. Never invent results, standards compliance, causal mechanisms, or real-world validity. Separate offered traffic from achieved throughput. Report loss/censoring with received-packet latency distributions.

Update canonical docs rather than creating conflicting accounts, and maintain links in the root README, `docs/README.md`, and `docs/MISSIONS.md`. Update `docs/DOCUMENTATION-AUDIT.md` and the relevant mission report. A mission remains INCOMPLETE until its implementation/blocker, verification, evidence, documentation, reproduction instructions, audit, and checklist are complete.

## Version control and data integrity

After each completed mission, audit staged paths, sizes, credentials, generated artifacts, and upstream source trees; make a descriptive Git commit and push to `main` unless the researcher explicitly says otherwise. Inspect remote history and use only safe fast-forward-compatible reconciliation. Never force-push, delete prior evidence, switch branches as a workaround, or commit credentials, simulator source/build trees, virtual environments, or large generated output. Record commit and remote verification in the report.

Before significant downloads/builds/runs, check free space. Keep the O-RAN simulator in a separate, explicitly pinned environment. Never copy legacy NR-U/ns-3.35/NR-v1.2 patches into the modern environment.
