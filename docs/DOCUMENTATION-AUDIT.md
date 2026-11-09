# Documentation audit

**Audit date:** 2026-11-09. **Status:** migration audit complete; no simulator installation or run performed.

## Evidence checked

- Historical root `manifests/commits.txt`, nested source Git revisions/status, tracked patches, file size and SHA-256 comparison of the root SQLite DB against archived Mission 2 data.
- Historical repository clean and synchronized at `997641ad294fab5040b5b5c556a40ecd6ba91879` before migration edits.
- Authenticated GitHub account is `kirolossedra`; target O-RAN repository was created public and its final commit is verified on `main`.
- Current upstream ib-ORAN README/install/KPI docs, ns-3 tags, CTTC release announcement/roadmap, and ns3-ai repository checked for versions and interfaces.
- Host compiler, Python, CMake, Boost, pybind11, yaml-cpp, protobuf package presence and free disk space checked.

## Verified claims

- Exact legacy stack commits and legacy patches are listed in [migration report](missions/mission-0-migration.md) and historic manifest.
- Two ns-3 installations under a different project were identified and retained; shared/uncertain host dependencies were retained.
- ib-ORAN guide documents the selected ns-3.48 + NR v5.1 + ns3-ai main + Python 3.11+ combination and dependency minima; see [compatibility](COMPATIBILITY.md).
- No modern source/build artifacts or simulation results exist in this repository at audit time.

## Unverified or future validation

- Actual compilation/runtime compatibility of the combined pinned sources (not performed by scope).
- Mobility support in a specific ib-ORAN scenario.
- Any latency, throughput, PRB or packet-loss result; none is claimed.
- Exact full topology/path and KPI code behavior until pinned source is installed and inspected.
- O-RAN repository is published at `https://github.com/kirolossedra/oran-publication`; initial scaffold commit is `4952d832af2d233a6c1ad5adef3e96a59256ef73`. Completion metadata and migration report are included in the final `main` commit.
- Historical archive migration was pushed to `https://github.com/kirolossedra/nru-publication` at `a9212edd9ecb17a12a3cd0ded6729e51210d8b19`.
- The owned local legacy source/build tree was removed after archive verification. Disk available space changed from 17 GiB to 20 GiB; mission raw outputs remained in place.

GitHub trees and local worktrees were checked after push; both local `main` commits matched their remote `main` SHAs and both worktrees were clean. No full simulator install/build was performed.

## Link and format checks

Before publication, validate relative Markdown links, JSON syntax, code fences/Mermaid blocks, absence of source trees/credentials/large files, and all citations. Keep this audit updated as claims gain evidence.
