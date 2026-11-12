# G1 load-calibration method and evidence

**Mission:** RA-ENG-005 / [issue #18](https://github.com/kirolossedra/oran-publication/issues/18). **Status:** bounded engineering calibration complete; final formal factors require researcher approval.

## What the pilot measures

Each configured UDP flow is identified from its source/destination tuple and FlowMonitor FlowId. Packet telemetry records unique application TX and RX identities. The summary reports configured rate, generated payload rate, delivered goodput, unique packet counts, missing-by-sink-stop count, and received-packet delay quantiles with sample count. Quantiles use nearest-rank `ceil(q*n)`, one-based, over received unique packets only. Packets that are not received before sink stop are not included in delay quantiles and are not automatically called physical-layer loss.

Applied-grant records describe scheduler allocations delivered to the PHY: RNTI, direction, time/slot, allocated RBG/PRB count, MCS, transport-block bytes, HARQ values and bitmap. The PRB sum is not airtime or unique spectrum. dApp MAC-demand snapshots record buffer bytes, CQI, achievable rate and actual throughput at controller opportunities. An RNTI mismatch is preserved as an unmatched grant; it is never silently assigned to a UE using guesswork.

## Fixed probe matrix

All four scenarios use seed 11, one gNB/six UEs, fixed positions, LOS, 10 MHz at 3.5 GHz, numerology 1, the same TDD pattern, RoundRobin dApp with `k=1`, Bypass xApp, 512-byte UDP payloads, a 1–8 s source interval, and a 9 s sink stop in a 10 s run.

| Case | UE 0 UL/DL | UEs 1–5 UL/DL |
|---|---|---|
| target-only | 20/20 kbps | no offered application traffic |
| low-six | 20/20 kbps | 20/20 kbps |
| DL-contending | 20/20 kbps | 20 kbps UL / 6 Mbps DL |
| UL-contending | 20/20 kbps | 6 Mbps UL / 20 kbps DL |

The 20 kbps and 6 Mbps values are researcher-authored campaign candidate levels. This seed-11 pilot supplies engineering evidence only. It does not set final research thresholds or combine UL and DL high-load conditions.

## Observed pilot results

The committed [per-UE CSV](../../results/RA-ENG-005/per-ue-load-calibration.csv) contains 38 flow rows. The [summary JSON](../../results/RA-ENG-005/summary.json) records 448 UL-case applied grants whose RNTIs did not match the end-of-run flow map. The direction-separated figures show configured offer as black ticks and received goodput as bars: [DL](../../results/RA-ENG-005/g1-load-calibration-dl.png) and [UL](../../results/RA-ENG-005/g1-load-calibration-ul.png).

All 12 low-six flows delivered 32/32 packets, at about 18.7 kbps per flow. In DL-contending, each UE1–3 generated 9,868 packets and received 18 by sink stop; their received P95 is about 7.02 s (`n=18` per UE). UE4 and UE5 received 9,860 and 9,868 packets, with about 5.77 Mbps delivered goodput and 3,923 and 3,788 mapped DL grants. UE0 DL delivered 2/32 packets. Buffer snapshots reached 10,157 bytes for heavily offered DL UEs. In UL-contending, UE1 and UE2 generated 9,868 packets each and received none by sink stop; UE3–5 received 9,340, 9,507 and 9,561 packets. These are observed values from one seed; no uncertainty interval or significance claim is supported.

The DL case is source-evidenced contention: large generated offers coexist with large buffer samples and divergent achieved goodput/applied grants. The UL case also has generated-versus-received divergence and queue evidence for UEs3–5, but RNTI churn prevents full per-UE grant attribution. Neither run proves physical saturation, stable long-term performance, or a causal policy effect. Application delay includes the modeled backhaul.

## Run and reproduction records

Configs are in `configs/scenarios/g1-loadcal-*.yaml`; checked runner is `scripts/run_g1_load_calibration.py`; joins are in `scripts/analyze_g1_load_calibration.py`; plots are reproduced by `scripts/plot_g1_load_calibration.py`. Full failed/successful stdout, effective configs, XML, demand samples, packet/grant tables, cleanup record and SHA256SUMS are retained under ignored `simulator/logs/RA-ENG-005-20261112/`. See the [mission report](../missions/RA-ENG-005-load-calibration.md) for exact commands, pins, failure handling, results and limitations.

## Candidate handoff

Carry 20 kbps per UE/direction as a low-load candidate and 6 Mbps for UEs1–5 in one direction at a time as a high-load candidate into a multi-seed confirmation pilot. Keep UE0 at 20 kbps both directions. Researcher approval is still needed for final factors, thresholds, sample count and formal protocol.
