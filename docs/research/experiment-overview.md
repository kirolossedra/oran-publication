# G1: NR scheduling under selective channel and traffic variation

**Research question:** How do selective UE6 NLOS, controlled motion and
independent UL/DL offered loads change *actual* NR MAC grants, redistribution
among six UEs, throughput/PDR and received-only P95/P99 application delay?

**Scientific status:** candidate incremental gap, **not** proven publication
novelty. Literature comparison and a validated five-seed experiment are still
required. One 5G-LENA gNB serves six UEs with `RoundRobin` versus greedy
`TopKCqi` (`k=1`, xApp `Bypass`), both UL/DL measured per run.

Design: 2 radio states (all LOS vs UE6 NLOS) × 2 mobility states
(stationary vs controlled linear motion) × 4 loads
(light, high both directions, DL-high, UL-high) × 2 policies ×
5 paired seeds (11, 22, 33, 44, 55) = **160 cells**.
See [exact configured values](../../configs/experiment.json).

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

## Revised target: high-throughput and ultra-reliable operation

The researcher rejected the former **6 Mbps/UE** high load as inadequate. We are now investigating whether **high delivered throughput can coexist with near-lossless delivery and controlled latency** when one UE experiences selective NLOS. The protocol config uses **100 MHz** NR and a provisional **50 Mbps/UE** busy-direction load (up to 300 Mbps offered per direction across six UEs), with a 1 Mbps/UE control. These are **not measured achievements or approved final rates**. Before freezing the full matrix, calibrate candidate per-UE offered loads **10, 25, 50, 100 Mbps** using actual delivered goodput, measured TX rate, per-UE PDR/loss, CQI, MCS, queues, MAC allocations and latency. Compare both schedulers, including their starvation behavior, at feasible and overloaded points.

An exploratory **99.999% PDR** target is a goal, not evidence of URLLC compliance. The existing 20-second simulations, single sanity seed, and lack of an approved deadline cannot establish five-nines confidence. Report packet counts, confidence limits, received-only latency and any true deadline misses; do not call the observed high-rate mode ultra-reliable until it is demonstrated. The full 160-arm experiment remains on hold pending calibration and researcher approval.
