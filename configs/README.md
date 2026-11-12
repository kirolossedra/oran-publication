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
