# Documentation audit

**Last updated:** 2026-11-11. **Status:** historical migration audit retained; Mission 1 installation/build/baseline audit added; current RA-ENG-001 source audit appended below.

## RA-ENG-001 source feasibility audit

**Audit date:** 2026-11-11. **Status:** documentation complete for the source-only audit; mission remains **INCOMPLETE** because the expected ignored `simulator/` tree is absent and bounded runtime probes were not possible.

### Evidence checked

- Repository issue #14 F1–F6 requirements, parent scientific scope in issue #12, and roadmap decision gates in issue #23; no stale issue #1–#10 was edited.
- Environment manifest pins and exact public source files at the recorded ib-ORAN, ns-3 and NR v5.1 revisions. Findings are line-linked in the [capability matrix](research/RA-ENG-001-capability-matrix.md).
- Host OS, CPU/RAM, Python/tool presence, disk space, branch, clean status and local presence/absence of `simulator/`.
- Updated README/docs navigation, mission index, Mermaid source-grounded diagram, relative Markdown links and source/claim labels.

### Source-verified findings

- Pinned NR helper exposes global `LOS` and `NLOS` condition factories. The default ib-ORAN UMi setup uses `Default` and sets both ThreeGpp channel-condition and channel-model update periods to zero.
- Pinned ns-3 ThreeGpp condition model caches condition per node pair and does not recompute it when update period is zero. The small-scale ThreeGpp channel model also disables updates at zero. The propagation-loss model still calculates from current endpoint positions; no movement trace was run.
- The Buildings condition model evaluates endpoint positions and LOS obstruction per pair. One-link selective geometry is a plausible **small-patch option**, not a verified probe result.
- ib-ORAN hardcodes RandomWalk2d, 0.83 m/s and random initial UE locations; it seeds the simulation but has no configurable fixed/controlled mode or retained trajectory series.
- The scheduler interface carries per-UE and per-direction CQI/buffer/rate state and actions. The xApp max-RBG value is an upper bound; dApp actions and C++ MAC grant/DCI paths are distinct.
- Current per-UE UL/DL endpoints exist, but per-direction rate/packet size and app lifecycle values are shared across UEs; transmission uses finite dataset payloads.
- Standard KPIs derive aggregate mean latency from FlowMonitor delay sums; cleanup removes `.flowstats`; the current app does not preserve per-packet TX/RX timestamps and identity for P95/P99.

### Observed, unverified and limitations

- **OBSERVED at mission start:** workspace was clean at `39d37ebfca594bb59640477484f0fbb476f998f0` on `main`, with 512 GiB free and no `simulator/` directory. The current working tree contains only the documentation changes listed in the mission report.
- Docker CLI 29.4.1 is present, but socket access is denied; Podman and `/dev/kvm` are absent; `ip` cannot inspect netlink in this session.
- **UNVERIFIED:** no build/runtime, building-geometry probe, repeatable trajectory check, applied-grant comparison, traffic pilot, or packet trace was run. Historical Mission 1 documentation is not a current local observation.
- No source code, configuration, simulator environment, or raw experiment data was changed or generated. No scientific novelty, industrial validity, causal effect, or performance result is claimed.

### Documentation and delivery state

- Report, matrix, options and architecture diagram are linked from root README, docs README and mission index.
- Staged-set audit passed for 8 Markdown paths (53,002 bytes total; largest file 17,206 bytes); no credential-pattern match, generated artifact, binary, or upstream source/build tree is staged. Local commit `36d11a44c023ef7ce5e24a8bfc78576516bdc0c0` was created; push failed because Git could not read a GitHub username. GitHub API checked remote `main` before and after the push attempt and confirmed it remains at `39d37ebfca594bb59640477484f0fbb476f998f0`. Researcher decision gates are listed in the report and technical-options doc.

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

Before Mission 1 publication, the final repository-local scan checked relative Markdown links and fenced code blocks in all 31 Markdown documents. Mermaid blocks were manually inspected for GitHub-compatible fenced structure. A Mermaid renderer was not available in the environment, so renderer-level parsing remains unverified. manifests/environment.json parsed with Python's JSON parser; `git diff --check` passed. Result SHA-256 entries verified against the preserved local source artifacts. Staged audit passed for 23 files (74,814 bytes): no file exceeded 2 MB, binary file or credential pattern was found, and no simulator/source/build path was staged. YAML config and KPI schema parsed; result hashes matched preserved source artifacts; staged diff whitespace check passed after correcting one Markdown line break. Mission commit ed4d272be7e04f61083b1e748a7846bf20a6746a was pushed to main; git ls-remote origin refs/heads/main returned the same SHA, and the worktree was clean immediately after that push.
