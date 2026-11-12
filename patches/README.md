# Patches

No simulator patches are carried from the historical NR-U project. Any necessary local patch must be minimal, justified, saved here as a reproducible diff, and tied to exact upstream commits.

- [RA-ENG-002 radio/mobility patch](RA-ENG-002-radio-mobility.patch): applies to Orange ib-ORAN commit `3ea5046389f0eb993cdf01ef6d6d33017e6921bb` inside the pinned ns-3.48 / NR v5.1 stack. It adds cell-wide forced LOS/NLOS selection, fixed and controlled-moving modes, sampled state traces, and no-application-flow validation support. The exact source pins and replay procedure are in the [RA-ENG-002 report](../docs/missions/RA-ENG-002-radio-mobility.md).
