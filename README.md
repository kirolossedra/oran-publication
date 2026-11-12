# O-RAN integrated six-UE research campaign

This repository snapshot contains the current integrated campaign package in [`campaigns/20261111-g1-integrated-v2/`](campaigns/20261111-g1-integrated-v2/). The folder name identifies the campaign and separates it from earlier run artifacts.

The study compares all-LOS with selective UE6 NLOS, stationary with controlled linear mobility, four UL/DL load arms, and RoundRobin with TopKCqi ib-ORAN dApp policies across five seeds. The matrix has 160 planned cells.

The campaign is still **in progress**. At this package snapshot, 92 cells had successful exits, zero had recorded nonzero exits, two incomplete attempts were preserved, and 68 cells had not completed. No campaign-wide results are claimed here. The earlier v1 packet PDR/latency outputs were invalidated because `PacketTag` did not provide unique packet identity; the v2 package uses a serialized application header.

The exact runner, analysis code, configuration, full editable source copies for every modified ib-ORAN file, status limitations, and reproduction commands are in the [campaign package README](campaigns/20261111-g1-integrated-v2/README.md). The [upstream source map](campaigns/20261111-g1-integrated-v2/UPSTREAM-SOURCES.md) links the complete ns-3, NR, ns3-ai, and ib-ORAN source at each pinned commit. Build products and raw simulation traces remain local.

## Mission and engineering records

- [Mission status and dependency ledger](docs/MISSIONS.md)
- [RA-ENG-004 packet/grant instrumentation report](docs/missions/RA-ENG-004-instrumentation.md)
- [RA-ENG-005 load calibration report](docs/missions/RA-ENG-005-load-calibration.md)
- [Packet/grant metric schema](docs/methodology/g1-packet-grant-metrics.md)
- [Documentation audit](docs/DOCUMENTATION-AUDIT.md)
- [Campaign v2 validation package](campaigns/20261111-g1-integrated-v2/README.md)

RA-ENG-004's bounded instrumentation validation is an engineering check, separate from the integrated v2 campaign. The campaign's own runner, full source overrides, and analyzer are the source for campaign results. The short RA-ENG-004 checks do not replace or augment the campaign dataset. No campaign-wide result is claimed until remaining cells, analysis, sample-count review, and documentation are complete.
