# Mission 0 — O-RAN migration preparation

**Status:** COMPLETE. Date: 2026-11-09.

## Objective, rationale, scope

Prepare a distinct research repository for O-RAN-based 5G RAN allocation work while preserving the NR-U project as a historical archive. Select an upstream-supported simulator stack. Acceptance: pinned compatibility documented; clean project scaffold and governance created; old archive updated without history rewrite; only owned obsolete source/build tree retired after remote preservation; both repositories pushed and verified. No simulator installation/build or experiment is in scope.

## Audit and ownership

Historical `self-research` was clean at `997641ad294fab5040b5b5c556a40ecd6ba91879`, synced to `kirolossedra/nru-publication` before migration edits. Its manifest records ns-3.35 commit `ac88b75eac1818c673cf2c939a96ac3005b1f051`, NR v1.2 line commit `fe0a1d2a5fb7d1547e46042041288a684893ba9e`, and NR-U commit `75a45143b1cd382326876a9597e856338673039a`. The local `source/ns-3-dev` checkout/build was separately audited as project-owned; patched source changes are represented by preserved patches in the archive. Source consumed about 3.2 GB and build about 2.9 GB; a root DB matched a tracked Mission 2 DB by SHA-256. Mission 3 raw outputs remain local and are not deleted. Two ns-3 trees in the separate `other-research/Research/OtherP/NR-U` project were identified and explicitly retained. System dependencies were retained because ownership is shared/uncertain.

## Selected modern stack

See [compatibility](../COMPATIBILITY.md) and [manifest](../../manifests/environment.json): ns-3.48, 5G-LENA v5.1, ns3-ai pinned main, ib-ORAN pinned main, Python 3.11+. The host's Boost 1.83 and pybind11 2.11.1 do not meet upstream minima; Python 3.11 and Protobuf development tools were not found. No dependency changes have been made.

## Proposed research scenario and architecture

One gNB serves a latency-sensitive UE and multiple background UEs with increasing UL/DL traffic. Compare baseline RAN allocation to modified policies; record per-UE latency, tail latency, throughput, loss, and PRB metrics. Numeric configurations remain intentionally unspecified. See [scenario diagram](../architecture/initial-scenario.md) and [methodology](../methodology/proposed-study.md).

## Changes and evidence

This mission created a separate repository scaffold, version manifest, governance, documentation, and decision records. It did not modify simulator protocol or source. The initial documentation commit is `4952d832af2d233a6c1ad5adef3e96a59256ef73`; the completed documentation/audit commit is recorded by the final remote `main` SHA. The historical archive update was pushed at `a9212edd9ecb17a12a3cd0ded6729e51210d8b19`. The project is reproducible as documentation by cloning `https://github.com/kirolossedra/oran-publication` at `main` and checking `manifests/environment.json`; no simulator command exists yet.

## Known limitations / unresolved

No modern stack has been installed, compiled, or smoke-tested. Mobility is available in upstream ns-3/NR generally, but support in the chosen ib-ORAN scenario remains unverified. Build compatibility of the pinned complete source set remains to be tested.

## Publication and local retirement verification

- Public project: `https://github.com/kirolossedra/oran-publication`; initial commit above, final `main` SHA recorded after this completion update is pushed.
- Historical archive: `https://github.com/kirolossedra/nru-publication`; migration commit `a9212edd9ecb17a12a3cd0ded6729e51210d8b19` is confirmed on remote `main`.
- Removed only the verified owned `/home/kiro/other-files/self-research/source/ns-3-dev` tree (3.2 GB measured before removal); free space rose from 17 GiB to 20 GiB. Retained local Mission 3 raw results (9.8 MB), other-project ns-3 trees, and shared packages.
- Both project worktrees were clean and their local `main` matched remote `main` at verification; no force push or branch change was used.
- The staged O-RAN tree contained only the 26 intended small text files; there were no source trees, build artifacts, credential patterns, or files above 10 MB. JSON and relative links validated; Mermaid syntax was not renderer-validated.

## Completion checklist

- [x] Separate repository and documentation structure published
- [x] Archive status and migration report pushed to historical repository
- [x] Legacy project-owned simulator tree retired after preservation verification
- [x] Unrelated simulator trees and shared dependencies retained
- [x] Version, host prerequisites, uncertainties, and no-install boundary documented
- [x] Links, manifest, staged paths/sizes, and worktree synchronization verified
