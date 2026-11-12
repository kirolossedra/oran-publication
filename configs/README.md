# Configuration index

**Authoritative study matrix:** [experiment.json](experiment.json).
The provisional campaign is g1-high-throughput-reliability-v1: one gNB,
six UEs, 100 MHz NR, all LOS vs selective UE6 NLOS, stationary vs
controlled motion, 1 Mbps/UE control and 50 Mbps/UE busy-direction offer,
RoundRobin vs greedy TopKCqi, and five paired seeds. Both UL and DL are
measured in all 160 planned cells. The 50 Mbps load is not PI-selected.
The required 8-cell all-LOS rate calibration runs first; the 160-cell
matrix remains gated on PI review.

[Focused scenarios](scenarios/README.md) are older engineering
instrumentation/calibration/scheduler checks and **not** separate versions
of the current study. Effective per-run configs are saved in ignored
run-specific directories. Do not alter declared experiment factors to
make a software bug less visible.
