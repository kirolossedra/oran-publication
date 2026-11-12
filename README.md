# O-RAN integrated six-UE research campaign

This repository snapshot contains the current integrated campaign package in [`campaigns/20261111-g1-integrated-v2/`](campaigns/20261111-g1-integrated-v2/). The folder name identifies the campaign and separates it from earlier run artifacts.

The study compares all-LOS with selective UE6 NLOS, stationary with controlled linear mobility, four UL/DL load arms, and RoundRobin with TopKCqi ib-ORAN dApp policies across five seeds. The matrix has 160 planned cells.

The approved 160-cell campaign completed locally on 2026-11-12: 160 cells have complete measurements using the corrected source hashes; seven earlier failed/interrupted pilot attempts are preserved and excluded. The analyzed raw run tree remains ignored and local. Curated outputs, per-UE results, paired-seed uncertainty, condition audits, and figures are under [`results/RA-ENG-008-20261112-audited-v3/`](results/RA-ENG-008-20261112-audited-v3/). The earlier v1 packet PDR/latency outputs remain excluded because `PacketTag` did not provide unique packet identity; the v2 package uses a serialized application header.

The exact runner, analysis code, configuration, full editable source copies for every modified ib-ORAN file, status limitations, and reproduction commands are in the [campaign package README](campaigns/20261111-g1-integrated-v2/README.md). The [upstream source map](campaigns/20261111-g1-integrated-v2/UPSTREAM-SOURCES.md) links the complete ns-3, NR, ns3-ai, and ib-ORAN source at each pinned commit. Build products and raw simulation traces remain local.

## Mission and engineering records

- [Mission status and dependency ledger](docs/MISSIONS.md)
- [RA-ENG-004 packet/grant instrumentation report](docs/missions/RA-ENG-004-instrumentation.md)
- [RA-ENG-005 load calibration report](docs/missions/RA-ENG-005-load-calibration.md)
- [RA-ENG-006 stock scheduling report](docs/missions/RA-ENG-006-stock-scheduling.md)
- [RA-ENG-006 stock policy source controls and observed probe](docs/research/g1-stock-policy-controls.md)
- [RA-ENG-007 paired campaign approval and readiness report](docs/missions/RA-ENG-007-paired-campaign.md)
- [RA-ENG-008 per-UE analysis report](docs/missions/RA-ENG-008-data-analysis.md)
- [RA-ENG-008 statistical method](docs/methodology/g1-statistics.md)
- [G1 claim/evidence/limit matrix](docs/research/g1-claim-evidence-matrix.md)
- [RA-ENG-008 curated outputs and figures](results/RA-ENG-008-20261112-audited-v3/)
- [RA-ENG-005 load-calibration method and results](docs/methodology/g1-load-calibration.md)
- [RA-ENG-005 per-UE summary and DL/UL figures](results/RA-ENG-005/)
- [Packet/grant metric schema](docs/methodology/g1-packet-grant-metrics.md)
- [Documentation audit](docs/DOCUMENTATION-AUDIT.md)
- [Campaign v2 validation package](campaigns/20261111-g1-integrated-v2/README.md)

RA-ENG-004's bounded instrumentation validation is an engineering check, separate from the integrated v2 campaign. The campaign's own runner, full source overrides, and analyzer are the source for campaign results. The short RA-ENG-004 checks do not replace or augment the campaign dataset. The technical campaign and analysis are complete; researcher review is still required for scientific interpretation, novelty, and any publication package.

**Scheduler audit update:** The [v2 campaign package](campaigns/20261111-g1-integrated-v2/README.md#independent-scheduler-and-analysis-corrections-2026-11-11) includes fixes for RoundRobin's 10.24-second service-history defect, TopKCqi equal-score tie bias, CQI input-state observability, campaign provenance, and analysis accounting. These fixes change policy behavior; earlier run artifacts remain excluded from corrected campaign results.
