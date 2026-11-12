# Documentation audit

**Last updated:** 2026-11-12. **Status:** historical migration audit retained; Mission 1 installation/build/baseline audit added; RA-ENG-001 source-feasibility audit complete; RA-ENG-002 bounded radio/mobility validation complete; KIRO portfolio execution in progress.

## KIRO portfolio execution preflight

Issue #24 was fetched from the connected GitHub account and confirmed open, titled “KIRO”. Its objective is the full O-RAN mission portfolio. Before further issue-24 implementation, the [portfolio execution report](missions/KIRO-issue-24-execution.md) was created from the mission template and records scope, dependencies, acceptance criteria, architecture, approval gates, and a conceptual dependency diagram. Local `docs/MISSIONS.md`, root README, and docs navigation link the report. Issues #1–#10 are excluded as stale per later researcher-owned RA-GAP-001 (#12) and RA-PLAN-001 (#23); active engineering issues are #14–#22. Formal protocol and manuscript stages remain gated by explicit researcher decisions in their issue bodies.

The [RA-ENG-002 mission report](missions/RA-ENG-002-radio-mobility.md) was created from the template before new source inspection or implementation. It records the previously selected whole-cell LOS/NLOS and mobility scope. The RA-ENG-001 report was reconciled against issue #14: its source-feasibility criteria are complete, and issue #14 was closed as completed on 2026-11-12. The Buildings-based per-UE path remains explicitly unverified. RA-ENG-002's patch, paired scenario configs, full no-traffic runs, mobility modes, trace checks, and limitations are now documented; issue #15 closure follows verified publication.

This preflight/reconciliation delivery stages eight Markdown paths only (78,410 bytes total; largest file 23,815 bytes). The audit checked 67 relative Markdown links (all targets exist), `git diff --cached --check`, staged path names, file sizes, credential patterns, and simulator/source/build/cache paths; no credentials, generated/binary artifacts, or simulator/source paths were staged.

## RA-ENG-001 source feasibility audit

**Audit date:** 2026-11-12. **Status:** **COMPLETE as a source-feasibility audit**. The exact pinned source tree, C++ build, existing Mission 1 scenario evidence, isolated probes, and pinned CPU Torch environment are recorded. This audit does not claim a loaded G1 campaign.

### Evidence checked

- Repository issue #14 F1–F6 requirements, parent scientific scope in issue #12, and roadmap decision gates in issue #23; no stale issue #1–#10 was edited.
- Environment manifest pins and exact public source files at the recorded ib-ORAN, ns-3 and NR v5.1 revisions. Findings are line-linked in the [capability matrix](research/RA-ENG-001-capability-matrix.md).
- Host OS, CPU/RAM, Python/tool presence, disk space, branch and initial absence of `simulator/`; exact local source pin verification, dependency restoration, C++ build and Python bridge import.
- Updated README/docs navigation, mission index, Mermaid source-grounded diagram, relative Markdown links and source/claim labels.

### Source-verified findings

- Pinned NR helper exposes global `LOS` and `NLOS` condition factories. The default ib-ORAN UMi setup uses `Default` and sets both ThreeGpp channel-condition and channel-model update periods to zero.
- Pinned ns-3 ThreeGpp condition model caches condition per node pair and does not recompute it when update period is zero. The small-scale ThreeGpp channel model also disables updates at zero. The propagation-loss model still calculates from current endpoint positions; the isolated movement probe did not measure propagation metrics.
- The Buildings condition model evaluates endpoint positions and LOS obstruction per pair. One-link selective geometry is a plausible **small-patch option**, not a verified probe result.
- ib-ORAN hardcodes RandomWalk2d, 0.83 m/s and random initial UE locations; it seeds the simulation but has no configurable fixed/controlled mode or retained trajectory series.
- The scheduler interface carries per-UE and per-direction CQI/buffer/rate state and actions. The xApp max-RBG value is an upper bound; dApp actions and C++ MAC grant/DCI paths are distinct.
- Current per-UE UL/DL endpoints exist, but per-direction rate/packet size and app lifecycle values are shared across UEs; transmission uses finite dataset payloads.
- Standard KPIs derive aggregate mean latency from FlowMonitor delay sums; cleanup removes `.flowstats`; the current app does not preserve per-packet TX/RX timestamps and identity for P95/P99.

### Observed, unverified and limitations

- **OBSERVED at mission start:** workspace was clean at `39d37ebfca594bb59640477484f0fbb476f998f0` on `main`, with 512 GiB free and no `simulator/` directory. Exact manifest commits were later cloned and verified; the `ns3iboran_nr` build, protobuf objects, Python bridge module, and Python imports succeeded. DNS resolution failed for both the official PyTorch CPU index and its alternate CDN, leaving the pinned Torch pair uninstalled; the failure log is under ignored `simulator/logs/RA-ENG-001-restore-20261111/`.
- Docker CLI 29.4.1 is present, but socket access is denied; Podman and `/dev/kvm` are absent; `ip` cannot inspect netlink in this session.
- **OBSERVED:** `nr-channel-setup-test`, `mobility-trace`, and `three-gpp-propagation-loss-model` passed. An isolated C++ probe queried all six gNB↔UE pairs and observed six LOS results with the LOS helper and six NLOS results with the NLOS helper. Two separate seed 1/run 1 probe invocations produced identical UE positions at 0, 60 and 130 seconds. The probe is not the full ib-ORAN environment and does not verify its RNG stream ordering. No full-scenario execution, applied-grant comparison, traffic pilot, or packet trace was run. Historical Mission 1 campaign results are not new results from this audit.
- No tracked upstream source or configuration file was modified and no research outcome dataset was generated. The ignored local scratch probe and two stdout logs are preserved under `simulator/`; the ignored local CMake cache was temporarily set to `NS3_EXAMPLES=OFF` for target construction, then restored to `NS3_EXAMPLES=ON`. The researcher selected whole-cell LOS/NLOS and mobility. No scientific novelty, industrial validity, causal effect, or performance result is claimed.
- The continuation audit refreshed the report and matrix with per-factor `GO` / `CONDITIONAL` / `BLOCKED` verdicts, exact pinned `ConstantVelocity` / `Waypoint` options, UE-to-EPC-to-NR application path, and a recommended nearest-rank estimator with per-cell sample counts for later packet tails. These are source-backed engineering recommendations, not a selected scientific protocol.
- At the initial retry, the router DNS server (`192.168.1.1`) failed public lookups. A temporary systemd-resolved per-link DNS-over-TLS setting using `1.1.1.1` resolved PyTorch and GitHub names. PyTorch index requests timed out over HTTPS, including direct CDN addresses; PyPI returned 404 for the exact `2.9.1+cpu` torch version. Initial pip/connectivity outputs are preserved in ignored `simulator/logs/RA-ENG-001-restore-20261112/`.
- **Observed follow-up:** the Aliyun PyTorch CPU mirror served the exact locked CPython 3.12 wheels after the official index/CDN timeouts. `torch==2.9.1+cpu` and `torchvision==0.24.1+cpu` installed in the isolated venv. Torch SHA256 `7417d8c565f219d3455654cb431c6d892a3eb40246055e14d645422de13b9ea1` matches an independent lock record for the official wheel URL; torchvision SHA256 is `48ff40694812292f1f75cddb517f9eef224a2e8388798a0aa191e27bf159fc5d`. The runtime check imported both versions, reported `cuda_available False`, and completed a CPU tensor operation. Listing, download, installation, hash, and runtime evidence are preserved in `simulator/logs/RA-ENG-001-restore-20261112/`; wheel archives remain under ignored `simulator/tooling/pip-cache/`.
- **Acceptance reconciliation:** issue #14 requests a source-feasibility audit and bounded probes, not a loaded G1 campaign. F1–F6 source maps, the isolated whole-cell/mobility probe, exact pins, dependencies, limits, alternatives, and reproducibility evidence are documented. The per-UE Buildings route remains a source-supported but unprobed option, clearly identified as `UNKNOWN` at runtime; the recorded researcher choice is whole-cell LOS/NLOS with mobility. The subsequent RA-ENG-002 mission can therefore proceed on that recorded scope. No new grant-effect, traffic-load, or packet-tail result is claimed.
- `gh auth status` initially reported an invalid stored token. After device sign-in as `the3miaphysite3engineer3`, `gh auth setup-git` succeeded and all ten local commits pushed as a fast-forward. `git ls-remote` and local `HEAD` both verified `89b5c1bb2116bd8154a6387fdd9ab93164e96acf`; the worktree was clean.
- The DNS, download and GitHub-auth documentation stage contains four Markdown paths (64,811 bytes total; largest file 22,166 bytes). Fifteen local links resolved; staged whitespace, credential-pattern, file-type, size and upstream-tree checks passed.
- The push-verification documentation stage contains three Markdown paths (57,806 bytes total; largest file 22,136 bytes). Thirteen local links resolved; the staged set contains no credentials, generated files, or simulator/source/build paths, and `git diff --cached --check` passed.
- The official-index retry documentation stage contains three Markdown paths (55,276 bytes total; largest file 22,148 bytes). Staged inspection found no credentials, non-Markdown/generated files, source/build paths, or unrelated files; links and whitespace checks passed.
- Markdown validation checked 60 local links across the root README, docs navigation, mission report, matrix, technical options, and architecture diagram; all local targets exist. `git diff --check` passed. The probe source and two stdout logs remain ignored; this continuation stages documentation only.
- The prior continuation stage contained seven Markdown paths (71,313 bytes total; largest file 22,057 bytes). The set had no credential-pattern matches, binary/generated files, simulator/source/build paths, or unrelated files.
- The 2026-11-12 retry/documentation stage contains seven Markdown paths (72,354 bytes total; largest file 22,128 bytes). Staged-path inspection found no credential-pattern matches, non-Markdown/generated artifacts, simulator/source/build paths, or unrelated files; `git diff --cached --check` passed. The retry log remains ignored and local.

### Documentation and delivery state

- Report, matrix, options and architecture diagram are linked from root README, docs README and mission index.
- The CPU-wheel recovery documentation update stages seven Markdown paths (79,821 bytes total; largest file 23,444 bytes). The set contains no credentials, generated/binary artifacts, simulator sources/builds/caches, or unrelated paths; staged whitespace check passed. Wheel archives, environment, and full download logs remain ignored.
- Documentation commit `691df8f620a0c041c8af19af9137003a095dba59` is verified on remote `main`; `git rev-parse HEAD` and `git ls-remote origin refs/heads/main` matched, and the worktree was clean at verification.
- The main documentation update passed staged-set checks for five Markdown paths (33,941 bytes before that audit note). The follow-up status update passed staged-set checks for two Markdown paths (23,731 bytes before that audit note). The test-results update passed staged-set checks for three Markdown paths (31,313 bytes before this audit note). These sets contained no credential-pattern matches, generated artifacts, binaries, simulator sources/builds, or unrelated paths. Simulator sources, venvs, dependency caches, build products, and logs remain ignored. Historical Git pushes failed while credentials were unavailable; the full local stack was later pushed by fast-forward on 2026-11-12, with remote `main` verified at `89b5c1bb2116bd8154a6387fdd9ab93164e96acf`. Researcher choices and the remaining runtime gate are listed in the report and technical-options doc.

## RA-ENG-002 radio and mobility validation

**Audit date:** 2026-11-12. **Status:** implementation and bounded validation complete; publication/issue closure pending.

- The mission report was created before new source inspection/editing. The researcher-recorded whole-cell LOS/NLOS choice satisfies the issue's granularity gate. The patch applies to the exact pinned Orange ib-ORAN commit and adds condition selection, `Fixed` and `ControlledMoving` modes, trace output, typed config fields, scenario override support, and no-application-flow initialization.
- The final pinned `ns3iboran_nr` target built. Full seed 1/run 1 LOS and NLOS runs used the same deterministic 2×3 UE geometry, +x speed 0.83 m/s, duration 20 s and one-second samples. The validator confirmed 120 rows per arm, all six realized conditions, identical positions/node IDs/RNTIs, and the assigned six-RNTI set. Fixed-position and 2 s RandomWalk regression probes also completed. No application traffic or dataset model was used.
- Failures preserved: host ccache path read-only, CLIP model DNS failure, forced-model `UpdatePeriod` attribute abort, runner auto-build missing ccache environment, and the short-run t=2 sampling expectation. Each was resolved or correctly bounded; logs remain in the unique ignored run directory.
- No radio performance, pathloss, RSRP/SINR/CQI, treatment-effect, indoor-factory validity, or P95/P99 result is claimed. Trace output records actual channel class and geometry; invoking pathloss in the trace was avoided to prevent consuming propagation-model random state.
- Tracked reproduction artifacts are the pinned-source patch, four scenario configs, config materializer, pair validator, mission report, and methodology. Full generated traces/configs/KPI and animation outputs remain ignored under `simulator/logs/RA-ENG-002-20261112/`; a checksum manifest records them. The previous Mission 1 upstream smoke output is unchanged.
- The replay patch passed `git apply --unidiff-zero --check` and application in a clean detached worktree at the pinned ib-ORAN commit; reverse-check also passed against the local integrated ns-3 tree. The staged delivery excludes simulator sources, builds, caches, environments, and raw outputs. Seventy-seven relative Markdown links across the updated navigation/reports resolve; staged whitespace and credential-pattern checks passed.

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
