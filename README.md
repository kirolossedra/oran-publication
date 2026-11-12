# O-RAN research — PI-directed LOS/NLOS transition and O-RAN control

This repository is the **single tracked source of truth** for the O-RAN study.
The WSL workspace must have the same relative paths for all tracked files.
Only third-party simulator checkouts, builds, environments, secrets, raw runs
and generated reports are expected to exist locally without GitHub copies.

## Repository index

| Directory | What is happening there |
|---|---|
| [Research](docs/research/README.md) | Scientific question, experiment scope, comparison constraints |
| [Configurations](configs/README.md) | One 160-cell experimental matrix and older focused scenarios |
| [Experiment scripts](experiment-scripts/README.md) | **Live execution:** sanity, campaign, analysis, throughput and starvation |
| [Simulator](simulator/README.md) | Pinned upstream dependencies; tracked ib-ORAN modifications |
| [Tests](tests/README.md) | Python regression tests for scheduler and metrics |
| [Methodology](docs/methodology/README.md) | Definition and limitations of packet, CQI and MAC measurements |
| [Historical records](docs/history/README.md) | Completed missions, decisions and audits, **not live code** |
| [Results](results/README.md) | Reviewed calibration; other raw/generated results stay local |
| [Archive](archive/README.md) | Retired patches and obsolete deployment code |

## Current scientific direction

The active engineering path is a **target-moving UE6 LOS→NLOS→LOS transition** with a matched all-LOS arm, competing UEs, and actual programmable O-RAN xApp RBG bounds. The design is detailed in [new transition implementation](docs/research/los-nlos-transition-implementation.md); [issue #26](https://github.com/kirolossedra/oran-publication/issues/26) governs PI scientific choices. High-throughput targets, final QoS semantics, transition timing, bandwidth and scheduler k are **not yet numerically selected**. The old 160-cell G1 campaign remains archived in-place for evidence and should not be executed as the new program.

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

This command runs scheduler/unit tests, builds `ns3iboran_nr`,
then a **20-cell high-throughput sanity subset** with `tqdm`,
measuring each UE's DL/UL offered load, actual TX Mbps, received goodput
Mbps, MAC Mbps, PDR, P50/P95/P99, CQI/MCS, queues, grants and starvation.
It **does not** start the 160-cell research campaign.

[Agent instructions](AGENTS.md) ·
[Research protocol](docs/research/experiment-overview.md) ·
[Codex sanity issue #25](https://github.com/kirolossedra/oran-publication/issues/25)
