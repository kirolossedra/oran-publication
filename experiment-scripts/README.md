# Experiment execution index

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

## High-rate / reliability gate

The runner now applies NR settings from `configs/experiment.json` explicitly and uses a distinct campaign ID for the revised high-rate study. Preliminary busy-direction offered load: **50 Mbps per UE**, **100 MHz** NR, against a **1 Mbps/UE** control. Codex must calibrate 10/25/50/100 Mbps per UE (at least stationary/all-LOS one-seed matched policy pairs) **before treating 50 Mbps as the selected operating point**. The sanity CSV and JSON report observed PDR against the exploratory five-nines goal, while explicitly refusing to claim verified ultra-reliability or a missing latency deadline. Throughput and reliability must be evaluated jointly; do not extrapolate from offered load. Keep previous runs under their original campaign ID.
