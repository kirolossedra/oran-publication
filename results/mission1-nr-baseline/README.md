# Curated Mission 1 NR smoke-baseline evidence

This small, committed subset is copied from the complete local run at simulator/runs/20261109-nr-toy-ibTopKCqi-k3-seed5/. It is an installation/control smoke test, not a statistically meaningful research experiment.

- effective-runConfig.yaml: exact effective upstream configuration.
- kpi.json: upstream KPI JSON copied without numerical edits.
- source-artifact-sha256.txt: hashes of those files and the locally preserved full execution and dApp scheduler logs.

Complete execution log, saved dApp trace, exit marker, default pre-run config, NetAnim XML, recovered payloads, and build/install logs remain locally under ignored simulator/. Their run ID and paths are in the Mission 1 report. Upstream cleanup deletes the transient FlowMonitor XML after KPI extraction; it is not available in this run.

Observed in the source log: process exit status 0; six UEs and one gNB; 16 FlowMonitor UDP flows. The standard flow set had 72 transmitted packets and 71 received packets (one uplink flow had 3/4 received). Per-link aggregate PDR was 100.00% downlink and 95.83% uplink. The KPI's link-level average latency was 25.0503 ms downlink and 30.9464 ms uplink; throughput averaged 431.353 kbps downlink and 264.664 kbps uplink. Total throughput was 2588.12 kbps downlink and 1587.98 kbps uplink. These are one-run upstream smoke-test outputs, not evidence about the proposed workload or a causal policy effect. See the detailed KPI caveats and interpretation in docs/missions/mission-1-installation.md.
