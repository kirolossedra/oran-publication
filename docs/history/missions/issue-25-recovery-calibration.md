# Mission RA-ENG-010 — Issue #25 WSL recovery and G1 high-throughput calibration

**Status:** COMPLETE for the bounded scope of Issue #25. The PI's final operating-point choice and any 160-cell campaign remain gated. **Date:** 2026-11-12. **Issue:** https://github.com/kirolossedra/oran-publication/issues/25

## Objective and scope

Recover the canonical O-RAN checkout without damaging the existing workspace, reconcile the pinned simulator with tracked ib-ORAN overrides, execute the issue's minimal high-throughput reliability calibration before the 20-cell sanity, then run bounded sanity only. Preserve old runs and keep new outputs uniquely versioned.

The issue explicitly forbids starting the 160-cell campaign before PI review. Interpretation: the user's single-word “existing” reply retains the 160-cell matrix structure for later review; the issue's explicit stop gate still prohibits running it now. Calibration is the narrower authorized design: all-LOS, stationary, both policies, one matched seed, DL and UL measured together at 10, 25, 50, and 100 Mbps per UE. The 50 Mbps stress and 1 Mbps control are provisional engineering values, not selected scientific factors.

## Rationale, requirements, and acceptance criteria

- Preserve the original workspace and all raw runs; do not overwrite tracked files or data.
- Verify the fresh clone is clean and tracked paths match origin/main.
- Record dependency pins and inspect tracked override differences before applying.
- Configure campaign identity g1-high-throughput-reliability-v1, 100 MHz NR, 50 Mbps/UE busy-direction offer, and 1 Mbps/UE control.
- Run eight calibration cells first and report configured offer, application TX, received goodput, PDR/loss, actual grants, queue state, and received-packet P95/P99 with sample counts/censoring.
- Do not infer a final operating point or URLLC compliance from one-seed runs.
- Run the 20-cell one-seed sanity only after calibration, regression checks, source reconciliation, and successful build; never run 160 cells.
- Preserve raw logs/configs and write analysis to a new timestamped results directory.
- Update issue #25 with measured evidence. Do not push unreviewed changes.

Acceptance evidence: clean tracked checkout; source backup/hash record; passing tests/build; 8/8 calibration outputs/report; 20/20 sanity outputs/report; docs/index/audit updates; no data loss or full-campaign execution.

## Existing architecture and dependencies

The active stack is configs/experiment.json → experiment-scripts/run_campaign.py → local pinned ns-3.48 / NR v5.1 / ns3-ai / ib-ORAN → experiment-scripts/analyze_campaign.py. Tracked modified Orange source is simulator/overrides/iboran/model/; the local simulator is an ignored separate upstream checkout. The fresh clone is /home/george/research/oran-publication. The prior checkout is /home/george/oran-publication; the expected ~/research/oran-publication did not exist at recovery start, so that original path was preserved instead of renamed.

## Risks, alternatives, and decisions

- Recorded issue decision: do not start the full 160-cell campaign before the rate/reliability design is reviewed.
- Recorded issue design: all-LOS stationary matched policy pairs, four rates, both directions measured together.
- Observed environment: new clone initially lacked simulator/tooling. The old pinned installation has CPU-only PyTorch 2.9.1 and ample disk; it is reused by symlinks to avoid >9 GB duplication.
- Observed source difference: five installed override files originally differed from the tracked 13-file manifest. The sanity gate backed up those originals before applying current overrides.
- Further source audit found three pre-existing modified files outside the original override manifest: iboran-ran-common.h, iboran_run.py, and iboranConfig.yaml. Their diffs were reviewed, added to the canonical override package, and the manifest now covers all 16 modified source/config files. All 16 hashes match installed files. The other four local-only scenario YAML files remain untouched and were not used by this campaign.
- Risk: 100 MHz / numerology 1 approaches ib-ORAN's 264-PRB protocol limit; effective radio config and run completion were verified. No final scientific rate choice is inferred.
- Alternative: copying/moving the old workspace would disturb the active writable workspace and duplicate multi-gigabyte data; symlinks preserve it. The old 6.8 GB campaign and RA-ENG-007 logs remain at their original paths.

## Conceptual workflow

This diagram shows the required execution order, not the full campaign.

~~~mermaid
flowchart LR
  A[Preserve old checkout and raw data] --> B[Fresh clone and tracked parity]
  B --> C[Review and back up source differences]
  C --> D[Configure G1 high-throughput v1]
  D --> G[Tests and pinned target build]
  G --> E[8-cell rate reliability calibration]
  E --> H[20-cell bounded sanity]
  H --> I[Audit docs, hashes, outputs, issue]
  I -. PI review required .-> J[160-cell campaign remains gated]
~~~

## Environment and source verification

- **Observed:** fresh clone commit 7742cb78e741b4d9e6efa3b6d49c71e746df5433 matched origin/main when created; initial tracked worktree was clean.
- **Observed:** ns-3.48 pin d2add90b452d600cfb4859baed8e9ea633519447; 5G-LENA NR v5.1 cedceadda17392c90587fb9400eb9b1f8c236713; ns3-ai b8c9858294b1d6a7f122b5154a3ce25057a54740; Orange ib-ORAN 3ea5046389f0eb993cdf01ef6d6d33017e6921bb.
- **Observed:** Python 3.12.3; PyTorch 2.9.1+cpu; no CUDA; no simulator processes at recovery start; 484 GiB free.
- **Observed:** target ns3iboran_nr built successfully. One compiler warning remains in NetAnim setup at iboran-ran-common.cc:753 (signed/unsigned comparison).
- **Observed:** 19 Python tests passed before calibration and again in the resumed sanity gate.
- **Observed:** initial all-13 source check found five mismatches; original copies were saved under simulator/runs/g1-high-throughput-reliability-v1-sanity/20261112T190025Z-2551847/source-backups. After source closure review, 16 override files now hash-match the installed checkout.
- **Evidence:** source-closure-sha256.txt is in both raw run roots. Per-attempt artifact-sha256.txt files cover simulator logs/configs; complete-results-sha256.txt covers every generated calibration and sanity analysis file.

## Calibration results (observed; one-seed engineering evidence)

All 8 runs completed with status 0 at seed 11, all-LOS, stationary, 100 MHz, 20 seconds, and both UL/DL measured. Analyzer accepted 8/8 runs and emitted 96 per-UE/direction rows. Full detail, including CQI/MCS, queue, actual grants, PRB symbols, PDR/loss, and latency sample adequacy, is in the calibration per-UE CSV and immutable raw attempts under simulator/runs/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847/; analyzed outputs are under results/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847-reanalysis/.

At 50 Mbps/UE in both directions, six-UE configured offer was 300 Mbps per direction. RoundRobin actual application TX was 78.68 Mbps per direction; received goodput was 46.54 Mbps DL (aggregate PDR 59.15%, 131,828 lost/unreceived) and 15.36 Mbps UL (PDR 19.53%, 259,689 lost/unreceived). TopKCqi goodput was 26.01 Mbps DL (PDR 33.06%, 216,012 lost/unreceived) and 15.05 Mbps UL (PDR 19.13%, 260,972 lost/unreceived). At 100 Mbps/UE, RoundRobin delivered 46.84 Mbps DL at PDR 53.66%, and 15.43 Mbps UL at PDR 17.68%. These observed values do not support near-lossless delivery at those offers in this seed.

At 50 Mbps/UE RoundRobin, max-UE P95/P99 values were 25.765/26.526 ms DL and 41.275/41.499 ms UL. The values are maxima of six per-UE quantiles, not pooled quantiles. All six UEs had at least 1,000 received latency samples in RoundRobin cells. Application latency includes modeled backhaul. These data do not establish run-to-run uncertainty, the 99.999% goal, a final operating point, or URLLC compliance.

## Sanity results (observed; one-seed engineering evidence)

All 20 planned sanity cells exited 0 and had complete measurement joins. The verdict is PASS, with 20/20 valid cells, 240 per-UE/direction rows, 40 scenario/direction rows, no analyzer issues, zero RoundRobin starvation flags, and 76 TopKCqi backlogged-grant-gap flags at the 1-second diagnostic threshold. The 76 TopKCqi flags are preserved evidence about the greedy k=1 policy; they do not fail the configured verdict. The summary, throughput table, per-UE table, starvation table, channel audit, run audit, and machine verdict are under results/g1-high-throughput-reliability-v1-sanity/20261112T193407Z-2623612/.

For the 50 Mbps/UE bidirectional cells, six-UE offered load is 300 Mbps per direction. RoundRobin produced 78.68 Mbps measured application TX, 46.54 Mbps received DL goodput (Jain 0.998) and 15.36 Mbps UL goodput (Jain 0.999) in all-LOS stationary contention. TopKCqi delivered 26.01 Mbps DL and 15.05 Mbps UL with Jain goodput 0.333 in both directions and four zero-goodput UEs. In the selective UE6-NLOS stationary case, RoundRobin delivered 46.54 Mbps DL and 15.65 Mbps UL; TopKCqi remained 26.01 Mbps DL and 15.05 Mbps UL. The report includes all six UEs, both directions, per-UE PDR/loss, received latency tails and sample counts, CQI/MCS, queue occupancy, actual applied grants, PRB share, first grant, and backlogged grant gaps.

**Interpretation:** In this single-seed sanity, the configured 50 Mbps/UE busy offer materially exceeds measured received goodput, especially in UL. TopKCqi k=1 gives lower aggregate goodput and many grant-gap flags; these are observed engineering results, not a general scheduler ranking or causal publication claim. The PI selects any final research operating point.

## Failures, troubleshooting, and preserved outputs

The first analyzer attempt failed after all eight calibration runs because resolving the reused runs symlink made attempts appear outside the fresh clone. Its partial output is preserved under results/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847/. The analyzer now retains the clone's logical path, and successful reanalysis is in a separate ...-reanalysis directory. No calibration run was repeated.

The 20-cell sanity resumed with the completed calibration report and passed. Calibration and sanity raw data use distinct timestamped roots and the new campaign ID. The old 20261111-g1-integrated-v2 6.8 GB run and RA-ENG-007 logs remain at /home/george/oran-publication and were not written by this run.

## Reproduction

Fresh full bounded execution from repository root:

~~~bash
bash experiment-scripts/sanity.sh --apply-overrides
~~~

If the eight calibration runs completed but analyzer repair is needed, resume the sanity phase with the already completed analysis:

~~~bash
bash experiment-scripts/sanity.sh --apply-overrides --calibration-analysis-dir results/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847-reanalysis
~~~

The completed calibration raw directory is simulator/runs/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847. Its analysis directory is results/g1-high-throughput-reliability-v1-calibration/20261112T190025Z-2551847-reanalysis. The completed sanity raw and analysis directories are simulator/runs/g1-high-throughput-reliability-v1-sanity/20261112T193407Z-2623612 and results/g1-high-throughput-reliability-v1-sanity/20261112T193407Z-2623612. Per-cell scenario.yaml, run-metadata.json, execution.log, packet events, actual MAC grants, demand and CQI traces are preserved.

## Limitations and unresolved research decisions

The calibration and sanity each use one run seed (11). Packets are measurements within a run, not independent simulation replicates. The calibration is fixed all-LOS/stationary; the sanity includes the bounded channel/mobility checks but cannot establish causal effects or infer five-seed uncertainty. P99 with fewer than 1,000 received samples is flagged exploratory. The issue's 99.999% PDR target is not established; no URLLC or application-deadline claim is made. The application deadline is unspecified and application delay includes modeled backhaul. Final operating rates and any full matrix require PI review.

## Documentation completion checklist

- [x] Objective, scope, rationale, acceptance, architecture, risks and alternatives documented
- [x] Configuration, runner, analyzer, source closure and their effects documented
- [x] Dependencies, versions, effective radio/rate parameters, commands and seed documented
- [x] Tests/build, calibration, sanity, failures and troubleshooting documented
- [x] Raw outputs preserved under unique paths with checksums
- [x] Mermaid workflow diagram labeled conceptual
- [x] Root README, docs README, mission index and documentation audit updated
- [x] Reproduction commands and output paths checked
- [x] Tracked-path, staged-size, credential, generated-artifact and upstream-source audit completed
- [x] Issue #25 updated with measured results
- [x] No 160-cell campaign run
- [x] No push performed because the issue forbids pushing unreviewed local changes
