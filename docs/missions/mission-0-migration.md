# Mission 0 — O-RAN migration preparation

**Status:** IN PROGRESS pending publication and verified retirement. Date: 2026-11-09.

## Objective, rationale, scope

Prepare a distinct research repository for O-RAN-based 5G RAN allocation work while preserving the NR-U project as a historical archive. Select an upstream-supported simulator stack. Acceptance: pinned compatibility documented; clean project scaffold and governance created; old archive updated without history rewrite; only owned obsolete source/build tree retired after remote preservation; both repositories pushed and verified. No simulator installation/build or experiment is in scope.

## Audit and ownership

Historical `self-research` was clean at `997641ad294fab5040b5b5c556a40ecd6ba91879`, synced to `kirolossedra/nru-publication` before migration edits. Its manifest records ns-3.35 commit `ac88b75eac1818c673cf2c939a96ac3005b1f051`, NR v1.2 line commit `fe0a1d2a5fb7d1547e46042041288a684893ba9e`, and NR-U commit `75a45143b1cd382326876a9597e856338673039a`. The local `source/ns-3-dev` checkout/build was separately audited as project-owned; patched source changes are represented by preserved patches in the archive. Source consumed about 3.2 GB and build about 2.9 GB; a root DB matched a tracked Mission 2 DB by SHA-256. Mission 3 raw outputs remain local and are not deleted. Two ns-3 trees in the separate `other-research/Research/OtherP/NR-U` project were identified and explicitly retained. System dependencies were retained because ownership is shared/uncertain.

## Selected modern stack

See [compatibility](../COMPATIBILITY.md) and [manifest](../../manifests/environment.json): ns-3.48, 5G-LENA v5.1, ns3-ai pinned main, ib-ORAN pinned main, Python 3.11+. The host's Boost 1.83 and pybind11 2.11.1 do not meet upstream minima; Python 3.11 and Protobuf development tools were not found. No dependency changes have been made.

## Proposed research scenario and architecture

One gNB serves a latency-sensitive UE and multiple background UEs with increasing UL/DL traffic. Compare baseline RAN allocation to modified policies; record per-UE latency, tail latency, throughput, loss, and PRB metrics. Numeric configurations remain intentionally unspecified. See [scenario diagram](../architecture/initial-scenario.md) and [methodology](../methodology/proposed-study.md).

## Changes and evidence

This mission creates a separate repository scaffold, version manifest, governance, documentation, and decision records. It does not modify simulator protocol or source. Exact final included paths, commit IDs, removals, storage, and audit will be appended after remote verification. Reproduction of the documentation state: clone the repository at its published commit and inspect the manifest and reports; no simulator command exists yet.

## Known limitations / unresolved

No modern stack has been installed, compiled, or smoke-tested. Mobility is available in upstream ns-3/NR generally, but support in the chosen ib-ORAN scenario remains unverified. Build compatibility of the pinned complete source set remains to be tested. Mission completion requires successful publication and safe cleanup evidence.
