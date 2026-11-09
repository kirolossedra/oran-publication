# Documentation audit

**Audit date:** 2026-11-09. **Status:** migration audit retained; Mission 1 installation/build/baseline audit added below.

## Mission 1 evidence checked

- Exact four simulator source revisions and tag-object/peeled commit distinctions against local Git metadata and manifest.
- Dependency versions in local micromamba prefix and Python venv, CMake configure/build logs, Protobuf generation and binding build logs, Python import, full baseline execution log, exit-status marker, effective config, KPI JSON, dApp scheduler trace, and SHA-256 list.
- Pinned ib-ORAN KPI definitions and implementation for flow aggregation, RBG allocation ratio and decision times.
- README/navigation, mission template/report, Mermaid code blocks, relative links, small committed evidence inventory, and ignore boundaries.

## Mission 1 verified claims

- ns-3.48, NR v5.1, ns3-ai and ib-ORAN revisions match the recorded source commits. ns-3/NR tag objects are distinct annotated tag object identifiers; peeled commit IDs are separately recorded.
- Host Python 3.12.3 met documented >=3.11. The NR build completed successfully; generated binding was built and imported. No source patches were applied.
- The upstream NR baseline completed with status 0. Saved logs report shared-memory setup, both Python schedulers initialized, and nonzero scheduler decisions; dApp trace includes RNTI/PRB/MCS allocations.
- KPI JSON contains PDR, throughput, mean latency, jitter, RBG use and app decision times. Reported values are from the saved JSON and execution log and describe one upstream smoke run only.
- Upstream cleanup removes temporary FlowMonitor XML; no packet-level records or P95/P99 results remain.
- Full build and run outputs remain locally under ignored simulator/. Only a small effective config, raw KPI JSON copy, checksums and evidence note are tracked.

## Mission 1 unverified and future claims

- No P95/P99/P99.9, packet-level latency or per-packet loss accounting is available from the baseline KPI JSON.
- The baseline source configures RandomWalk2d UE mobility and the run uses it; no focused movement/trajectory validation or fixed-position comparison was performed.
- The xApp ran using Bypass; the run does not establish restrictive resource bounding or a policy benefit.
- No external RIC interoperability, standards conformance, industrial traffic validity, statistical conclusion or real-world deployment is claimed.
- Reproduction on a clean second host is not independently tested; model and package channel availability remain environment risks.
- Full build/run logs are preserved on the working machine but intentionally not hosted due their size. Their hashes are in the committed evidence subset; remote readers cannot retrieve the full local logs from GitHub.

## Migration-time audit (historical pre-Mission 1 state)

The following subsection records the state at the end of migration preparation, before Mission 1 installation. Its “not performed” statements describe that earlier audit only.

### Evidence checked

- Historical root `manifests/commits.txt`, nested source Git revisions/status, tracked patches, file size and SHA-256 comparison of the root SQLite DB against archived Mission 2 data.
- Historical repository clean and synchronized at `997641ad294fab5040b5b5c556a40ecd6ba91879` before migration edits.
- Authenticated GitHub account is `kirolossedra`; target O-RAN repository was created public and its final commit is verified on `main`.
- Current upstream ib-ORAN README/install/KPI docs, ns-3 tags, CTTC release announcement/roadmap, and ns3-ai repository checked for versions and interfaces.
- Host compiler, Python, CMake, Boost, pybind11, yaml-cpp, protobuf package presence and free disk space checked.

### Verified claims

- Exact legacy stack commits and legacy patches are listed in [migration report](missions/mission-0-migration.md) and historic manifest.
- Two ns-3 installations under a different project were identified and retained; shared/uncertain host dependencies were retained.
- ib-ORAN guide documents the selected ns-3.48 + NR v5.1 + ns3-ai main + Python 3.11+ combination and dependency minima; see [compatibility](COMPATIBILITY.md).
- No modern source/build artifacts or simulation results existed at the migration audit time.

### Unverified at migration audit time

- Actual compilation/runtime compatibility of the combined pinned sources (not performed by scope).
- Mobility support in a specific ib-ORAN scenario.
- Any latency, throughput, PRB or packet-loss result; none is claimed.
- Exact full topology/path and KPI code behavior until pinned source is installed and inspected.
- O-RAN repository is published at `https://github.com/kirolossedra/oran-publication`; initial scaffold commit is `4952d832af2d233a6c1ad5adef3e96a59256ef73`. Completion metadata and migration report are included in the final `main` commit.
- Historical archive migration was pushed to `https://github.com/kirolossedra/nru-publication` at `a9212edd9ecb17a12a3cd0ded6729e51210d8b19`.
- The owned local legacy source/build tree was removed after archive verification. Disk available space changed from 17 GiB to 20 GiB; mission raw outputs remained in place.

GitHub trees and local worktrees were checked after migration publication; both local `main` commits matched their remote `main` SHAs and both worktrees were clean at that time. No full simulator install/build had yet been performed then.

## Current Mission 1 publication checks

Before Mission 1 publication, a repository-local scan checked relative Markdown links and fenced code blocks in all Markdown files; all 31 documents present at the initial pass succeeded. Four decision records and the source lock manifests were added afterward and are included in a final repeat scan. Mermaid blocks were manually inspected for GitHub-compatible fenced structure. A Mermaid renderer was not available in the environment, so renderer-level parsing remains unverified. manifests/environment.json parsed with Python's JSON parser; `git diff --check` passed. Result SHA-256 entries verified against the preserved local source artifacts. Staged audit passed for 23 files (74,552 bytes): no file exceeded 2 MB, binary file or credential pattern was found, and no simulator/source/build path was staged. YAML config and KPI schema parsed; result hashes matched preserved source artifacts; staged diff whitespace check passed after correcting one Markdown line break.
