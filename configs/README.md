# Configuration index

**Authoritative study matrix:** [experiment.json](experiment.json).
The design has one gNB, six UEs, all LOS vs selective UE6 NLOS,
stationary vs controlled motion, light / bidirectional high / DL-high /
UL-high traffic, RoundRobin vs greedy TopKCqi, and five paired seeds.
Both UL and DL are measured in all 160 cells.

[Focused scenarios](scenarios/README.md) are older engineering
instrumentation/calibration/scheduler checks and **not** separate versions
of the current study. Effective per-run configs are saved in ignored
run-specific directories. Do not alter declared experiment factors to
make a software bug less visible.

## Provisional high-rate redesign

The 6 Mbps busy-direction loads have been replaced by a **provisional 50 Mbps/UE** stress point, with **1 Mbps/UE** low-rate control and **100 MHz** NR bandwidth. The exploratory offered-load sweep candidates are **10, 25, 50, 100 Mbps/UE** (not guaranteed delivered rates). The high-load values are **not final protocol approval**; calibrate capacity, loss, grants and latency before the complete 160-cell design is authorized. The desired 99.999% PDR is an aspirational target requiring confidence and sufficient duration; no application latency deadline has been chosen.
