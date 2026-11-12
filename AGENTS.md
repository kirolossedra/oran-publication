# Agent contract — O-RAN research

## First: preserve repository parity

The root [README](README.md) and the index of **every directory** explain
the canonical layout. Every version-controlled file must be at the **same
relative path in WSL and GitHub**. Do not recreate the obsolete date-based
`campaigns/` package or a second `scripts/` folder.

**Tracked files:** `configs/`, `experiment-scripts/`, `tests/`,
`simulator/overrides/iboran/`, `docs/`, `archive/`, and reviewed
`results/calibration/`. **Ignored/local files:** external third-party
`simulator/ns-3.48/` (including nested upstream Git repositories), installed
`simulator/tooling/`, build products, venvs, raw runs, logs, generated
reports and secrets. See [simulator index](simulator/README.md).

Modified Orange ib-ORAN code has **one tracked home**:
`simulator/overrides/iboran/model/`. The ignored upstream simulator
checkout receives copied files only when a run is prepared; it is not an
independent authoritative implementation. Keep `SHA256SUMS` current.
Never silently edit a local installed copy without updating the tracked file.

## Critical first task: recover and reconcile WSL

A previous Codex agent reported `.git` empty in the WSL project. Follow
[workspace reconciliation](docs/workspace-reconciliation.md):
inspect processes/status, preserve the old workspace and its local research
outputs, clone GitHub into a separate clean sibling, compare changed code,
restore pinned dependencies safely, then establish one working checkout with
tracked-file parity. **Do not issue `git pull` into a broken checkout**,
`git reset --hard`, force-push, delete raw evidence, or silently overwrite
local edits. Do not switch the active branch without researcher approval.

Repair a non-destructive environment problem rather than declaring scientific
work blocked. Stop and ask only where preserving the research data cannot be
guaranteed.

## Execute sanity before expensive experiments

After synchronization and while simulator processes are idle:

```bash
bash experiment-scripts/sanity.sh --apply-overrides
```

The command validates and backs up source overrides, runs tests, rebuilds
only `ns3iboran_nr`, then runs an eight-cell matched all-LOS stationary
rate calibration at 10/25/50/100 Mbps per UE before it executes a **20-case
one-seed** subset with `tqdm`. It analyses the calibration and all sanity
UE/direction outputs, and emits
`sanity-summary.md`, `sanity-throughput-by-scenario.csv`,
`sanity-per-ue.csv`, `sanity-starvation.csv`, and
`sanity-verdict.json` in isolated timestamped locations.
See [experiment-scripts index](experiment-scripts/README.md).

**Throughput is mandatory:** configured offered Mbps, measured application
TX Mbps, received goodput Mbps, MAC actual/achievable Mbps, six-UE sums and
Jain fairness, independently in UL and DL. Also report TX/RX packets,
PDR/loss, P50/P95/P99 latency with reception sample sizes/censoring,
reported CQI vs ambiguous missing feedback, MCS, queue occupancy,
actual applied grants, PRB share, time to first grant and longest
backlogged period without a grant. Use actual MAC grants, not scheduled intent.

RoundRobin's 10.24-second frame-wrap bug was corrected but needs WSL
verification. TopKCqi with `k=1` is greedy and may starve UEs by design:
investigate rather than silently forcing fairness. A 1-second backlogged
grantless gap is a diagnostic threshold, not a 3GPP guarantee.
Keep original and modified policy runs in **separate cohorts**.
No 160-cell campaign until bounded sanity is reviewed by the PI.

## Scientific governance

The researcher owns hypotheses, experiment factors, interpretation and
publication claims; agents optimize the **system** and evidence pipeline,
not people or convenient-looking results. Keep uncertainty explicit.
Do not mislabel end-to-end application delay as pure RAN latency or
undefined received latency as zero. Raw runs/configs/logs must remain
immutable and uniquely versioned. Do not invent novelty or statistics.

Work in one integrated recover → build → sanity → audit iteration,
fixing routine failures without proliferating missions or approval gates.
Maintain all directory README indexes whenever files move.
Historical reports under [docs/history](docs/history/README.md) are evidence,
not the current execution manual. [Issue #25](https://github.com/kirolossedra/oran-publication/issues/25)
is the active Codex handoff; update it with actual measurements, not promises.
