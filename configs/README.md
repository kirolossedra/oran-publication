# Configuration index

**Current, opt-in design:** [los-nlos-transition.json](los-nlos-transition.json): one gNB/six UEs, selected mobile UE6, within-run LOS→NLOS→LOS, fixed all-LOS matched baseline, programmable xApp control. Unknown scientific quantities are null pending PI decision; these must not be filled by Codex. See [issue #26](https://github.com/kirolossedra/oran-publication/issues/26).

**Legacy campaign matrix (not current scientific direction):** [experiment.json](experiment.json).


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
