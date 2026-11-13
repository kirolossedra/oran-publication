# O-RAN research — PI-directed LOS/NLOS transition and O-RAN control

This repository is the **single tracked source of truth** for the O-RAN study.
The WSL workspace must have the same relative paths for all tracked files.
Only third-party simulator checkouts, builds, environments, secrets, raw runs
and generated reports are expected to exist locally without GitHub copies.

## Repository index

| Directory | What is happening there |
|---|---|
| [Research](docs/research/README.md) | Scientific question, experiment scope, comparison constraints |
| [Configurations](configs/README.md) | Provisional 160-cell matrix plus bounded reliability calibration |
| [Experiment scripts](experiment-scripts/README.md) | **Live execution:** sanity, campaign, analysis, throughput and starvation |
| [Simulator](simulator/README.md) | Pinned upstream dependencies; tracked ib-ORAN modifications |
| [Tests](tests/README.md) | Python regression tests for scheduler and metrics |
| [Methodology](docs/methodology/README.md) | Definition and limitations of packet, CQI and MAC measurements |
| [Historical records](docs/history/README.md) | Completed missions, decisions and audits, **not live code** |
| [Results](results/README.md) | Reviewed calibration; other raw/generated results stay local |
| [Archive](archive/README.md) | Retired patches and obsolete deployment code |

## Current scientific direction

The active engineering path is a **target-moving UE6 LOS→NLOS→LOS transition** with a matched all-LOS arm, competing UEs, and actual programmable O-RAN xApp RBG bounds. The design is detailed in [new transition implementation](docs/research/los-nlos-transition-implementation.md); [issue #26](https://github.com/kirolossedra/oran-publication/issues/26) governs PI scientific choices. High-throughput targets, final QoS semantics, transition timing, bandwidth and scheduler k are **not yet numerically selected**. The old 160-cell G1 campaign remains archived in-place for evidence and should not be executed as the new program.

The [issue #26 prior-work, provenance, and run-readiness review](docs/research/los-nlos-prior-work-and-run-readiness.md) summarizes related literature and the decisions/evidence still needed.

```bash
python experiment-scripts/run_los_nlos_transition.py --plan-only
# After PI fills the required JSON values and WSL is provisioned:
python experiment-scripts/prepare_los_nlos_transition.py --apply-overrides --build
python experiment-scripts/run_los_nlos_transition.py --limit 2
```

## Legacy G1 recovery and diagnostics (not current experiment)

**The Git checkout in WSL was reported broken (empty `.git`).**
Before pulling or building, follow the
[safe workspace reconciliation guide](docs/workspace-reconciliation.md).
Do not blindly pull into that directory or overwrite local experiment data.

After parity is restored and the installed simulator is idle, run:

```bash
bash experiment-scripts/sanity.sh --apply-overrides
```

The command validates source overrides, runs regression checks and builds
`ns3iboran_nr`, then runs the one-seed eight-cell all-LOS rate calibration
(10/25/50/100 Mbps/UE, both policies and UL/DL) before the **20-cell
high-throughput sanity subset**
with `tqdm`. It reports offered load, application TX, received goodput,
MAC throughput, PDR/loss, received-only P50/P95/P99 with sample counts,
CQI/MCS, queues, applied grants and starvation. Calibration values are
engineering evidence only; the PI chooses scientific operating rates.
It **does not** start the 160-cell research campaign.

[Current mission status](docs/MISSIONS.md) ·
[Issue #25 mission report](docs/history/missions/issue-25-recovery-calibration.md) ·
[Documentation audit](docs/DOCUMENTATION-AUDIT.md)

[Agent instructions](AGENTS.md) ·
[Research protocol](docs/research/experiment-overview.md) ·
[Codex sanity issue #25](https://github.com/kirolossedra/oran-publication/issues/25)
