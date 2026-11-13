# Documentation audit — issue #25 recovery, calibration and sanity

**Status:** COMPLETE for bounded issue scope. **Updated:** 2026-11-12. **Issue:** https://github.com/kirolossedra/oran-publication/issues/25.

## Checkout and preservation

The fresh clone is /home/george/research/oran-publication at initial commit 7742cb78e741b4d9e6efa3b6d49c71e746df5433, equal to origin/main when cloned. The prior checkout remains intact at /home/george/oran-publication because the requested ~/research/oran-publication path was absent before recovery. The clone reuses ignored simulator/ns-3.48, simulator/runs, and simulator/logs via symlinks; tooling/activate.sh points to the pinned venv. No prior tracked file was overwritten by the clone. The previous 6.8 GB run and RA-ENG-007 diagnostics remain under their existing IDs.

## Versions and source parity

Pinned dependencies: ns-3.48 d2add90b452d600cfb4859baed8e9ea633519447; NR v5.1 cedceadda17392c90587fb9400eb9b1f8c236713; ns3-ai b8c9858294b1d6a7f122b5154a3ce25057a54740; Orange ib-ORAN 3ea5046389f0eb993cdf01ef6d6d33017e6921bb. Python is 3.12.3 and PyTorch is 2.9.1+cpu. Available space before execution was 484 GiB.

Source review found five mismatches in the original 13-file override manifest. Their installed copies were backed up to simulator/runs/g1-high-throughput-reliability-v1-sanity/20261112T190025Z-2551847/source-backups before synchronization. A broader ib-ORAN status audit found three further pre-existing modified files outside that manifest: iboran-ran-common.h, iboran_run.py, and iboranConfig.yaml. Their full source/config files were added to the canonical overlay; simulator/overrides/iboran/SHA256SUMS now records 16 files. All 16 overlay files hash-match the installed Orange tree. Four local-only scenario YAML files under the upstream checkout were not used or overwritten.

## Tests and simulator build

The in-gate Python regression suite passed 19/19 before calibration and 19/19 again on resume. ns3iboran_nr built successfully; one signedness warning remains at iboran-ran-common.cc:753 in NetAnim setup. Reused build was clean on the second gate.

## Calibration and sanity evidence

Calibration: 8/8 matched cells, seed 11, stationary all-LOS, 100 MHz, 20 s, two policies, four rates (10/25/50/100 Mbps/UE in both directions). Analyzer accepted all eight and emitted 96 UE/direction rows. At 50 Mbps/UE, RoundRobin six-UE goodput was 46.54 Mbps DL (PDR 59.15%, 131,828 lost/unreceived) and 15.36 Mbps UL (PDR 19.53%, 259,689 lost/unreceived); TopKCqi was 26.01 Mbps DL (PDR 33.06%) and 15.05 Mbps UL (PDR 19.13%). Full per-UE CQI/MCS, latency tails/sample counts, grants, PRB, queue and loss values are in the local calibration report/CSV.

Sanity: 20/20 cells exited 0 with complete measurements; analyzer verdict PASS, 240 UE/direction rows, 40 direction summaries, no audit issues, zero RoundRobin starvation flags, and 76 TopKCqi flags at the one-second diagnostic threshold. All per-UE throughput, PDR/loss, received latency P50/P95/P99 and adequacy, CQI/MCS, queue, grants, PRB, first-grant and backlog-gap outputs are preserved.

Raw calibration: simulator/runs/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847/. Calibration analysis: results/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847-reanalysis/. Raw sanity: simulator/runs/g1-high-throughput-reliability-v1-sanity/20261112T193407Z-2623612/. Sanity analysis: results/g1-high-throughput-reliability-v1-sanity/20261112T193407Z-2623612/. Every attempt has an artifact checksum list; both raw roots have source closure manifests; complete-results-sha256.txt covers generated analysis files.

The first calibration analysis failed after simulation because it resolved a symlink to the preserved checkout. Its partial output remains in a separate directory. The analyzer was fixed to retain logical paths; the completed eight runs were not repeated. The 20-cell sanity then resumed against the verified calibration directory and passed.

## Scientific boundary

These are one-seed engineering diagnostics, not publication inference. No final scientific rate is selected. The 50 Mbps/UE stress case falls far below near-lossless delivery in the observed UL and DL; the PI selects operating rates. A one-seed run cannot establish the exploratory 99.999% PDR goal or URLLC compliance. Delay is application one-way and includes modeled backhaul; no deadline was specified. The full 160-cell matrix was not run and remains gated on PI review.

## Repository and delivery audit

- Tracked source changes are limited to configuration, experiment scripts, tests, docs/indexes, mission template, and the reviewed ib-ORAN override package.
- Raw runs, logs, analysis, simulator checkout/build, and venv remain ignored local artifacts; no simulator tree or raw output is staged.
- Local link checks across updated Markdown files pass; git diff --check passes.
- Credentials/secrets, staged sizes, and local upstream-source tree are audited before the local commit.
- No push is made: Issue #25 explicitly forbids pushing unreviewed local changes. Verified results were posted in [issue comment 6835644818](https://github.com/kirolossedra/oran-publication/issues/25#issuecomment-6835644818); PI review is still required for any full campaign.
- Remote main was observed at 7ecc4342728a4a4ec5a3cbf9323bbb133b3cc8c7 during final audit; this local checkout is based on 7742cb78e741b4d9e6efa3b6d49c71e746df5433. No fetch/rebase/push was performed during finalization. The audited changes were committed locally as `f5514df` (parent `7742cb78e741b4d9e6efa3b6d49c71e746df5433`) and remain unpushed.
