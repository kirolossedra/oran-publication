# O-RAN integrated campaign: 20261111-g1-integrated-v2

This folder is the versioned code/configuration package for the integrated six-UE O-RAN study. It is distinct from the earlier `20261111-g1-integrated` run artifacts and from the NR baseline. The campaign ID is embedded in the configuration and output paths.

## Status snapshot

At packaging time, the local run manifest showed 90 of 160 planned matrix cells completed successfully, no recorded nonzero exits, and two incomplete attempt directories preserved. Seventy cells had not yet completed. These are execution counts, not research findings; the campaign and analysis remain incomplete.

Earlier v1 packet PDR and latency outputs are excluded because packet tags did not provide reliable per-datagram identity. The limitation is described in [`docs/INSTRUMENTATION-LIMITATION.md`](docs/INSTRUMENTATION-LIMITATION.md). No raw simulation outputs are included in this package. They remain locally under `simulator/runs/20261111-g1-integrated-v2/` and must be retained with their run-specific logs.

## Contents

- `config/g1-integrated-campaign.json`: predeclared 160-cell matrix, traffic levels, seeds, geometry, and simulation parameters.
- `scripts/run_g1_integrated_campaign.py`: resumable runner. Each attempt is written to a unique directory.
- `scripts/analyze_g1_integrated_campaign.py`: packet/MAC data processing and paired-seed analysis.
- `patches/RA-ENG-G1-packet-observation.patch`: application header instrumentation against pinned Orange `ns3-iboran` commit `3ea5046389f0eb993cdf01ef6d6d33017e6921bb`.
- `docs/INSTRUMENTATION-LIMITATION.md`: explains why the earlier packet metrics are not used.

## Reproduction

The pinned ns-3.48, 5G-LENA, ns3-ai, and Orange ib-ORAN environment is installed separately under `simulator/` and is excluded from Git. After provisioning that environment and applying the recorded project patches, run from the repository root:

```sh
python3 campaigns/20261111-g1-integrated-v2/scripts/run_g1_integrated_campaign.py
python3 campaigns/20261111-g1-integrated-v2/scripts/analyze_g1_integrated_campaign.py
```

The runner uses `simulator/ns-3.48/.venv/bin/python`, resumes successful cells with the matching serialized-header schema, and writes raw artifacts to `simulator/runs/20261111-g1-integrated-v2/`. The analyzer writes processed tables and figures to `results/20261111-g1-integrated-v2/`. Do not infer final results from the status snapshot above.

## Measurement scope

Each run measures both DL and UL, all-LOS versus selective UE6 NLOS, stationary versus controlled linear movement, four offered-load arms, two ib-ORAN dApp UE-selection policies, and five matched seeds. Packet-level application delay includes the modeled backhaul and is not pure RAN scheduling delay. P99 summaries require sample-count review. Forced NLOS is a synthetic channel condition, not an obstacle-crossing model.
