# O-RAN integrated campaign: 20261111-g1-integrated-v2

This folder is the versioned code/configuration package for the integrated six-UE O-RAN study. It is distinct from the earlier `20261111-g1-integrated` run artifacts and from the NR baseline. The campaign ID is embedded in the configuration and output paths.

## Status snapshot

The approved matrix completed locally on 2026-11-12: 160 of 160 planned cells have complete measurements matching the corrected source hashes. Seven failed/interrupted pilot attempts are preserved and explicitly excluded. The final run audit and analysis live in the ignored local raw tree and curated results at `../../results/RA-ENG-008-20261112-audited-v3/`; raw simulator output is not committed. Counts indicate execution and data integrity, not scientific findings or novelty.

Earlier v1 packet PDR and latency outputs are excluded because packet tags did not provide reliable per-datagram identity. The limitation is described in [`docs/INSTRUMENTATION-LIMITATION.md`](docs/INSTRUMENTATION-LIMITATION.md). No raw simulation outputs are included in this package. They remain locally under `simulator/runs/20261111-g1-integrated-v2/` and must be retained with their run-specific logs.

## Contents

- `config/g1-integrated-campaign.json`: predeclared 160-cell matrix, traffic levels, seeds, geometry, and simulation parameters.
- `scripts/run_g1_integrated_campaign.py`: resumable runner. Each attempt is written to a unique directory.
- `scripts/analyze_g1_integrated_campaign.py`: packet/MAC data processing and paired-seed analysis.
- `source-overrides/`: complete, directly editable copies of every ib-ORAN source file modified for this campaign; these are full source files, not diffs. `SHA256SUMS` records their local contents.
- [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md): exact public source repositories and commits for ns-3, 5G-LENA NR, ns3-ai, and Orange ib-ORAN.
- `docs/INSTRUMENTATION-LIMITATION.md`: explains why the earlier packet metrics are not used.

## Reproduction

The full upstream library sources are available at the exact repositories and commits in `UPSTREAM-SOURCES.md`. The campaign's edited ib-ORAN files are included here as complete source copies. To restore them, copy `source-overrides/model/...` over the matching paths in `simulator/ns-3.48/contrib/iboran/`. The local build, virtual environment, logs, and raw runs are excluded. After provisioning the pinned environment and restoring the source copies, run from the repository root:

```sh
python3 campaigns/20261111-g1-integrated-v2/scripts/run_g1_integrated_campaign.py
python3 campaigns/20261111-g1-integrated-v2/scripts/analyze_g1_integrated_campaign.py
```

The runner uses `simulator/ns-3.48/.venv/bin/python`, resumes successful cells with the matching serialized-header schema, and writes raw artifacts to `simulator/runs/20261111-g1-integrated-v2/`. The analyzer writes processed tables and figures to the directory supplied via `--output-dir`; for the audited analysis see `results/RA-ENG-008-20261112-audited-v3/`. Do not infer scientific conclusions from execution counts.

## Measurement scope

Each run measures both DL and UL, all-LOS versus selective UE6 NLOS, stationary versus controlled linear movement, four offered-load arms, two ib-ORAN dApp UE-selection policies, and five matched seeds. Packet-level application delay includes the modeled backhaul and is not pure RAN scheduling delay. P99 summaries require sample-count review. Forced NLOS is a synthetic channel condition, not an obstacle-crossing model.

## Independent scheduler and analysis corrections (2026-11-11)

This GitHub package includes reviewed fixes for a **RoundRobin selection bug**:
previously served UEs were assigned stored monotonic service timestamps in
milliseconds while never-served UEs were initialized from the wrapping NR
frame/subframe counter. Several unserved UEs received their first grant only
after the 10.24-second SFN wrap. The corrected implementation prioritizes
never-served candidates, followed by the least recently served, using one
monotonic nanosecond time base.

TopKCqi remains greedy by primary metric. The patch changes only equal-score
tie breaking to least recently served then RNTI; it **does not** guarantee
fairness with `k=1` when CQIs differ. It is a **modified benchmark**, not the
unaltered upstream TopKCqi. CQI input-state changes are logged separately to
`logs/mac-cqi-input-state.csv` without modifying CQI/MCS control; DL CQI zero
is explicitly ambiguous, not conclusively proof of missing feedback.

The analyzer deduplicates directional-extension cells (160 unique scenarios,
not 240), selects attempts numerically, checks populated measurement files,
and rejects attempts recorded against different source hashes. The runner
includes both selection-policy files in per-attempt provenance. Prior runs
remain intact but **must not be pooled** with runs using these corrections.

To apply the committed code to the separate WSL simulator checkout, **after
stopping or finishing any active campaign**, sync the GitHub repository, then
copy the edited files from `source-overrides/model/` to the matching paths
under `simulator/ns-3.48/contrib/iboran/model/`. Rebuild the NR target and
run the regression suite:

```sh
python3 -m unittest discover -s campaigns/20261111-g1-integrated-v2/tests -v
cd simulator/ns-3.48
./ns3 build ns3iboran_nr -j 2
```

The GitHub package and local WSL simulator are distinct. The RA-ENG-007
report records the local post-fix compilation, source application, campaign
runs, and analysis evidence; a new device must apply the manifest, rebuild,
and reproduce runs before relying on local artifacts. `source-overrides/SHA256SUMS`
covers the corrected copied source files.
