# G1: NR scheduling under selective channel and traffic variation

**Research question:** How do selective UE6 NLOS, controlled motion and
independent UL/DL offered loads change *actual* NR MAC grants, redistribution
among six UEs, throughput/PDR and received-only P95/P99 application delay?

**Scientific status:** candidate incremental gap, **not** proven publication
novelty. Literature comparison and a validated five-seed experiment are still
required. One 5G-LENA gNB serves six UEs with `RoundRobin` versus greedy
`TopKCqi` (`k=1`, xApp `Bypass`), both UL/DL measured per run.

Design: 2 radio states (all LOS vs UE6 NLOS) × 2 mobility states
(stationary vs controlled linear motion) × 4 loads (1 Mbps/UE control,
50 Mbps/UE bidirectional busy, DL-high, UL-high) × 2 policies ×
5 paired seeds (11, 22, 33, 44, 55) = **160 planned cells**.
Rates and the 100 MHz NR configuration are provisional pending the
required one-seed 10/25/50/100 Mbps/UE all-LOS stationary calibration and
PI review. See [exact configured values](../../configs/experiment.json)
and [execution steps](../../experiment-scripts/README.md).

**Scientific controls:** pair UE6 LOS/NLOS at matched
seed/motion/load/policy, examine peer grant redistribution, measure
actual per-UE throughput and queue demand. A baseline all-LOS UE-to-UE
difference is not by itself a causal NLOS effect.
Application latency includes modeled backhaul, not just RAN delay.
Original PacketTag packet identity was invalidated. Current
serialized-header and corrected RoundRobin need WSL sanity validation;
TopKCqi starvation at `k=1` may be intrinsic.

**Next action:** first repair the WSL Git workspace; execute the
20-cell throughput/grant sanity and audit results before authorizing
the full campaign. See [entrypoints](../../experiment-scripts/README.md).
