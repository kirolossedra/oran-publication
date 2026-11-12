# Experiment execution index

All **current runnable research scripts** live here. Do not create a
second `scripts/` or `campaigns/<date>/scripts/` directory.

| File | Function and status |
|---|---|
| [sanity.sh](sanity.sh) | **Run first:** activate WSL environment, start bounded validation |
| [sanity.py](sanity.py) | Source checks/backups, tests, ns3 build, eight-cell reliability calibration, 20-cell runs and comprehensive report |
| [analyze_reliability_calibration.py](analyze_reliability_calibration.py) | Per-UE and six-UE DL/UL calibration report: delivery, latency, grants and queues |
| [run_campaign.py](run_campaign.py) | Resumable experiment runner with `tqdm`; `--sanity-block` or full 160 cells |
| [analyze_campaign.py](analyze_campaign.py) | PDR, latency, throughput, real grants, demand and matched contrasts |
| `run_load_calibration.py`, `analyze_load_calibration.py`, `plot_load_calibration.py` | Historical traffic calibration |
| `run_scheduler_probe.py`, `compare_scheduler_probe.py`, `reprocess_scheduler_probe.py` | Earlier policy-control probe |
| `map_udp_flows.py`, `analyze_packet_events.py` | Diagnostic packet/FlowMonitor joins |

Run from the **repository root** in the provisioned WSL checkout:

```bash
bash experiment-scripts/sanity.sh --apply-overrides
```

The gate validates and backs up source overrides, runs scheduler regressions,
builds the pinned target, then runs the matched one-seed all-LOS stationary
calibration at 10/25/50/100 Mbps per UE in both directions for both policies
(8 cells). It writes a separate report before starting the bounded 20-cell
sanity. The configured 50 Mbps
busy load and 1 Mbps control are provisional. Neither the calibration nor
sanity chooses the PI's final scientific operating point.

The 20-cell subset is one seed: stationary at all four configured loads,
both channel states and policies (16 cells), plus moving bidirectional
contention with both channel states/policies (4 cells); both UL and DL are
measured in every cell. This is engineering sanity, not a five-seed result.
No full 160-cell campaign is run by this command. If calibration completed
but its analysis needed repair, resume with
`bash experiment-scripts/sanity.sh --apply-overrides --calibration-analysis-dir <completed-analysis-dir>`;
the script validates the calibration report and skips those eight runs.

Raw outputs: ignored `simulator/runs/<campaign-id>-sanity/<timestamp>/`.
Analyzed outputs: ignored `results/<campaign-id>-sanity/<timestamp>/`.
The report includes **offered / TX / goodput / MAC throughput (Mbps)**,
six-UE totals and Jain fairness, packet delivery and P50/P95/P99,
CQI/MCS, queue backlog, applied grants, PRB shares, and starvation.
No full campaign before the PI reviews this evidence.
