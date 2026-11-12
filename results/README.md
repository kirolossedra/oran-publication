# Result storage and provenance

[calibration/](calibration/README.md) contains the reviewed small historical
traffic-calibration results that are intentionally tracked.

Current high-throughput sanity and the full 160-cell campaign generate
**local-only** results under `results/<campaign-id>/` and
`results/<campaign-id>-sanity/<timestamp>/`; raw traces under
`simulator/runs/` are also ignored. Do not overwrite or silently pool
results from the old and modified scheduling policies.
A committed analysis script does **not** establish a completed WSL test.
