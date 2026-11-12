# O-RAN integrated six-UE research campaign

This repository snapshot contains the current integrated campaign package in [`campaigns/20261111-g1-integrated-v2/`](campaigns/20261111-g1-integrated-v2/). The folder name identifies the campaign and separates it from earlier run artifacts.

The study compares all-LOS with selective UE6 NLOS, stationary with controlled linear mobility, four UL/DL load arms, and RoundRobin with TopKCqi ib-ORAN dApp policies across five seeds. The matrix has 160 planned cells.

The campaign is still **in progress**. At packaging time, 90 cells had successful exits, zero had recorded nonzero exits, two incomplete attempts were preserved, and 70 cells had not completed. No campaign-wide results are claimed here. The earlier v1 packet PDR/latency outputs were invalidated because `PacketTag` did not provide unique packet identity; the v2 package uses a serialized application header.

The exact runner, analysis code, configuration, source patch, status limitations, and reproduction commands are in the [campaign package README](campaigns/20261111-g1-integrated-v2/README.md). Raw simulation traces and the pinned simulator/build tree are not stored in GitHub; they remain in the local research workspace.
