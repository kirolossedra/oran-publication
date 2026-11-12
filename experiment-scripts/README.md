# Experiment execution index

## Current new O-RAN LOS→NLOS→LOS experiment

- [prepare_los_nlos_transition.py](prepare_los_nlos_transition.py): verify/preserve/backup/apply pinned source; optional tests and NR build WITHOUT launching old G1.
- [run_los_nlos_transition.py](run_los_nlos_transition.py): paired all-LOS/LOS→NLOS→LOS, six-UE target movement, dApp xApp controls, preserved attempts.
- [analyze_los_nlos_transition.py](analyze_los_nlos_transition.py): time-phase per-UE UL/DL TX-cohort delivery, P95/P99 and CQI (not physical loss or QoS guarantee).
- [Numeric decision gates](../configs/los-nlos-transition.json): no automatic 6/50/500 Mbps selection, no unstated bandwidth/time thresholds, no automatic k.

```bash
python experiment-scripts/run_los_nlos_transition.py --plan-only
# After PI selects parameters and WSL environment is installed:
python experiment-scripts/prepare_los_nlos_transition.py --apply-overrides --build
python experiment-scripts/run_los_nlos_transition.py --limit 2
```

## Legacy G1 scripts (preserved for reproducibility, NOT the current experiment)


All **current runnable research scripts** live here. Do not create a
second `scripts/` or `campaigns/<date>/scripts/` directory.

| File | Function and status |
|---|---|
| [sanity.sh](sanity.sh) | **Run first:** activate WSL environment, start bounded validation |
| [sanity.py](sanity.py) | Source checks/backups, tests, ns3 build, 20-cell runs and comprehensive report |
| [run_campaign.py](run_campaign.py) | Resumable experiment runner with `tqdm`; `--sanity-block` or full 160 cells |
| [analyze_campaign.py](analyze_campaign.py) | PDR, latency, throughput, real grants, demand and matched contrasts |
| `run_load_calibration.py`, `analyze_load_calibration.py`, `plot_load_calibration.py` | Historical traffic calibration |
| `run_scheduler_probe.py`, `compare_scheduler_probe.py`, `reprocess_scheduler_probe.py` | Earlier policy-control probe |
| `map_udp_flows.py`, `analyze_packet_events.py` | Diagnostic packet/FlowMonitor joins |

Run from the **repository root** in the provisioned WSL checkout:

```bash
bash experiment-scripts/sanity.sh --apply-overrides
```

First matched seed, stationary four loads with both channel states and
both schedulers (16 cells), plus moving bidirectional contention with
both states/schedulers (4 cells); **both UL and DL in every case**.
This is engineering sanity, not a five-seed research result.

Raw outputs: ignored `simulator/runs/<campaign-id>-sanity/<timestamp>/`.
Analyzed outputs: ignored `results/<campaign-id>-sanity/<timestamp>/`.
The report includes **offered / TX / goodput / MAC throughput (Mbps)**,
six-UE totals and Jain fairness, packet delivery and P50/P95/P99,
CQI/MCS, queue backlog, applied grants, PRB shares, and starvation.
No full campaign before the PI reviews this evidence.
