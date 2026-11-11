# RA-ENG-001 — Source-Verified G1 Feasibility Audit

**Status:** INCOMPLETE (pinned source restored and NR target built; isolated channel/mobility probe passed; full scenario, grant, traffic and packet-tail evidence remain incomplete). **Updated:** 2026-11-12. **GitHub:** [issue #14](https://github.com/kirolossedra/oran-publication/issues/14).

## Research objective and scope

Determine whether the pinned ns-3.48 / 5G-LENA v5.1 / ns3-ai / Orange ib-ORAN stack can support the G1 engineering factors at the required granularity: per-UE LOS/NLOS, repeatable UE movement, six-UE controls and traffic, and packet-level tail latency with actual RAN allocation evidence. Separate source-supported capabilities from capabilities observed in the Mission 1 smoke run. This is a feasibility audit, not a research campaign.

At mission start, the required source checkout under ignored `simulator/` was absent, so initial source findings used the exact pinned public revisions. The four repositories were subsequently restored at their manifest commits and the C++ target built. Runtime conclusions remain bounded to the isolated helper/mobility probe; the Python-controlled full scenario remains unavailable without the pinned CPU Torch wheels.

## Scientific motivation and hypotheses (human-owned)

The parent G1 question in [RA-GAP-001, issue #12](https://github.com/kirolossedra/oran-publication/issues/12) is a researcher-owned candidate about LOS/NLOS propagation and mobility under competing UL/DL load, scheduling-policy effectiveness, and per-user P95/P99 latency and allocation tradeoffs. Novelty and final hypotheses are not established by this engineering audit. **Researcher decision recorded 2026-11-11:** use whole-cell LOS/NLOS comparisons with mobility as the primary setup.

## Requirements and acceptance criteria

Follow the ordered F1–F6 audit and acceptance criteria in issue #14: establish global versus per-UE channel-condition feasibility; assess mobility and reproducibility; trace xApp/dApp actions to actual MAC grants; inspect per-UE and directional traffic controls; identify valid packet-tail instrumentation and censoring treatment; and report exact pins, dependencies, risks, and the smallest next validation probes. No full traffic system, analysis pipeline, policy comparison, or multi-factor campaign is in scope.

Acceptance evidence will be recorded separately for F1–F6. Claims will be tagged SOURCE-VERIFIED, OBSERVED, INFERRED, or UNKNOWN. The report remains INCOMPLETE if the pinned source or decisive feasibility evidence cannot be inspected.

## Existing architecture and affected components

**SOURCE-VERIFIED:** Mission 1 records a pinned ns-3.48 / NR v5.1 / ns3-ai / ib-ORAN stack, one gNB and six UEs, TDD at 3.5 GHz and 10 MHz, a Python xApp/dApp control path through ns3-ai shared memory, and an upstream toy-workload smoke run. The existing architecture map is [executed-baseline.md](../architecture/executed-baseline.md); source revisions are in [environment.json](../../manifests/environment.json). This audit checked the exact pinned source code for ib-ORAN and ns-3 plus the NR v5.1 channel helper.

**OBSERVED in this workspace:** at the post-build checkpoint, repository branch was `main`, six local commits ahead of `origin/main` at `39d37ebfca594bb59640477484f0fbb476f998f0`; the expected ignored `simulator/` directory was initially absent and has since been restored. Host is Ubuntu 24.04.4 x86_64, 20 logical CPUs, 30 GiB RAM (24 GiB available), 510 GiB free workspace filesystem before restoration, system Python 3.14.3, Python 3.12.3 at `/usr/bin/python3.12`, GCC 13.3.0, CMake 3.28.3, Ninja, and Conda. Docker CLI 29.4.1 is installed but access to `/var/run/docker.sock` is denied; Podman is absent; `/dev/kvm` is absent; `ip` cannot open a netlink socket in this execution environment.

Target source areas from issue #14 were inspected as documented in the [capability matrix](../research/RA-ENG-001-capability-matrix.md), [technical options](../research/RA-ENG-001-technical-options.md), and [signal-path diagram](../architecture/RA-ENG-001-signal-path.md): ib-ORAN NR environment/common setup, pinned NR channel helper, ns-3 condition and propagation models, orchestrator/Python schedulers, NR MAC scheduler/shared-memory interfaces, per-UE app setup, FlowMonitor aggregation/cleanup, and application packet handling.

## Implementation details and alternatives

No upstream simulator source was modified. The exact pinned source audit establishes: helper-level global forced LOS/NLOS is directly supported; selective link conditions are a small, unproven Buildings-geometry probe; default 3GPP condition and channel updates are disabled at period zero; and per-UE mobility, traffic, control and measurement paths have the limits recorded in the matrix. The researcher approved the whole-cell LOS/NLOS and mobility scope, resolving the scope gate. No different simulator, custom channel model, or copied legacy NR-U patch was used.

## Architecture/algorithm/workflow diagrams

See [RA-ENG-001 signal path](../architecture/RA-ENG-001-signal-path.md). Solid arrows are source-traced; dashed edges are proposed diagnostics, not implemented functionality.

## Changed files and reproducible patches

Tracked changes are documentation only: this report, the capability matrix, technical options, source-grounded signal-path diagram, root README navigation, docs navigation, mission index, and documentation audit. An ignored local scratch probe at `simulator/ns-3.48/scratch/ra_eng_001_cell_mobility_probe.cc` reproduces the pinned six-UE mobility block and queries the NR helper's channel-condition result for each link; it is not an ib-ORAN scenario modification, and no tracked upstream source was changed.

## Dependencies, versions, configuration, seeds, commands

Expected pins are documented in `manifests/environment.json`; exact upstream source refs are listed in the capability matrix. Sources were downloaded under the ignored `simulator/` path and checked out at ns-3 `d2add90b452d600cfb4859baed8e9ea633519447`, NR `cedceadda17392c90587fb9400eb9b1f8c236713`, ns3-ai `b8c9858294b1d6a7f122b5154a3ce25057a54740`, and ib-ORAN `3ea5046389f0eb993cdf01ef6d6d33017e6921bb`; `git rev-parse HEAD` matched each pin. The C++ prefix was restored from `manifests/cpp-environment-lock.txt`. Python 3.12.3 venv packages were installed from the frozen lock without dependency re-resolution, excluding `torch==2.9.1+cpu` and `torchvision==0.24.1+cpu`. The original router DNS (`192.168.1.1`) failed to resolve public names; a temporary `systemd-resolved` per-link DNS-over-TLS setting using `1.1.1.1` now resolves both PyTorch and GitHub hostnames. HTTPS requests to the official PyTorch index still time out, and direct access to its resolved CDN addresses also times out; the exact wheels remain unavailable. The official PyPI API returned 404 for the exact `2.9.1+cpu` release; the response is preserved at `simulator/logs/RA-ENG-001-restore-20261112/torch-pypi-exact-version.json`. Current install and CDN connectivity outputs are `torch-cpu-official-index-install.log` and `torch-cdn-connectivity.log` in that same run directory; earlier retry outputs are also preserved there. The original failed direct-wheel attempt remains under `simulator/logs/RA-ENG-001-restore-20261111/torch-cpu-wheel-download.log`. No package substitution was made. Configure commands used CMake with explicit Python 3.12 include/library paths and the venv's pybind11 3.1.0. Build commands: `./ns3 configure --enable-examples --enable-tests`; `./ns3 build ns3iboran_nr -j 4`; `ninja -C cmake-cache -j 4 proto-objects`; and `ninja -C cmake-cache -j 4 iboran_shm_structure_py_binding`. A local ccache directory/config under ignored `simulator/tooling/` was needed because the host ccache default config path is read-only. Docker daemon access and netlink inspection failed with permission errors; KVM and Podman were absent.

## Tests and verification evidence (logs/paths)

**Observed build and test verification:** the pinned `ns3iboran_nr` target completed successfully (1,035/1,035 Ninja steps); protobuf objects built (3/3); `iboran_shm_structure_py_binding` built (1,082/1,082 steps); and `from ns3ai_utils import Experiment` plus `import iboran_shm_structure_py_binding` succeeded in the Python 3.12.3 venv with the local C++ library path. The existing ns-3 suites `nr-channel-setup-test`, `mobility-trace`, and `three-gpp-propagation-loss-model` passed (0.013 s, 0.006 s, and 2.639 s). An isolated C++ probe reproduced the pinned gNB/UE mobility parameters and queried all six endpoint pairs: six of six returned LOS under the LOS helper and six of six returned NLOS under the NLOS helper. Two separate seed 1/run 1 invocations produced byte-identical UE positions at 0, 60 and 130 seconds. Outputs are `cell-mobility-probe-run1.log` and `cell-mobility-probe-run2.log` under the unique ignored log directory. This verifies the helper and movement block in isolation; it does not reproduce random stream ordering in the complete ib-ORAN environment or observe propagation metrics.

Reproduce the isolated probe from `simulator/ns-3.48/` with the recorded C++/Python environment configured:

```sh
cmake -S . -B cmake-cache -DNS3_EXAMPLES=OFF
CCACHE_CONFIGPATH=/home/george/oran-publication/simulator/tooling/ccache.conf CCACHE_DIR=/home/george/oran-publication/simulator/tooling/ccache ninja -C cmake-cache -j 4 scratch_ra_eng_001_cell_mobility_probe
CELL_PROBE_RUN_ID=replace-with-unique-id
CELL_PROBE_RUN_DIR=../logs/RA-ENG-001-cell-probe-${CELL_PROBE_RUN_ID}
test ! -e "$CELL_PROBE_RUN_DIR" && mkdir "$CELL_PROBE_RUN_DIR"
./build/scratch/ns3.48-ra_eng_001_cell_mobility_probe-default > "$CELL_PROBE_RUN_DIR/run1.log"
./build/scratch/ns3.48-ra_eng_001_cell_mobility_probe-default > "$CELL_PROBE_RUN_DIR/run2.log"
diff -u "$CELL_PROBE_RUN_DIR/run1.log" "$CELL_PROBE_RUN_DIR/run2.log"
cmake -S . -B cmake-cache -DNS3_EXAMPLES=ON
```

The probe fixes seed 1/run 1 and samples at 0, 60, and 130 seconds. The probe source SHA-256 is `1d59d57b1badcd8d35011277a1593c0ffc6f284f20ae8562515f89ec0d556f2f`; both output logs have SHA-256 `20765345e217f72bbe7a4d65ef167f202c97eca193debf393ea0dd1baa13a197`. Examples are restored to ON after the isolated build. The first binding configure selected host Python 3.14 and the system pybind11; it was reconfigured with Python 3.12 paths and venv pybind11 3.1.0. ccache first failed on the host's read-only `/home/george/.config`; subsequent builds used the ignored project-local cache. Building the test runner and probe with examples enabled encountered pinned ns3-ai example compilation errors; examples were temporarily disabled in the ignored cache and restored to `NS3_EXAMPLES=ON`. No upstream source file was patched. Reproducibility outputs (source pins, explicit C++ package list, Python freeze, import result, build/test/probe logs, and CPU-wheel download failure) are under `simulator/logs/RA-ENG-001-restore-20261111/`. No ib-ORAN scenario or campaign was run. Actual grant/traffic observations and packet-level tail measurement remain unverified. Both the official PyTorch CPU index and alternate download CDN failed DNS resolution, so the pinned CPU Torch wheels could not be retrieved.

## Raw data and result references

No performance dataset or campaign run was created. The isolated mobility/helper diagnostics are not research outcome data; their full output logs are preserved under the unique ignored run directory `simulator/logs/RA-ENG-001-restore-20261111/` and no previous evidence was overwritten.

## Analysis, sample sizes, uncertainty, interpretation

Not applicable to the source audit. No performance result or statistical claim is made.

## Limitations and unverified assumptions

- The pinned source and C++ build are now present under ignored `simulator/`; the exact CPU Torch and torchvision packages remain unavailable, so the complete Python runtime and campaign have not been validated.
- Host tool presence does not establish runtime behavior or container access. This session cannot connect to Docker, inspect network interfaces/routes through netlink, or use KVM/Podman.
- Mission 1 claims are recorded documentation evidence until reconciled with the manifest and any preserved local evidence available here.
- LOS/NLOS helper behavior and repeatable mobility are verified only in an isolated six-UE probe. Full-scenario condition/RNG behavior, grants, traffic, and packet-tail measurement remain unverified.

## Problems, failures, and resolutions

Initial obstacle: expected ignored simulator tree absent. Downloaded all four exact pinned repositories and restored the locked C++ dependencies and the available Python lock packages. The initial pip resolution selected CUDA-enabled Torch through an unpinned transitive dependency; it was stopped before CUDA packages installed. The router DNS server did not answer public DNS queries. A temporary systemd-resolved per-link DNS-over-TLS setting using Cloudflare at `1.1.1.1` restored hostname resolution, but TLS to the official PyTorch index and CDN still times out. The PyPI API does not list the exact `torch==2.9.1+cpu` version. Install and retry logs remain under ignored `simulator/logs/RA-ENG-001-restore-20261112/`; no substitute was installed. Build first failed on the host's read-only ccache config and used the local ignored cache on retry. Initial CMake selected Python 3.14 for ib-ORAN; it was reconfigured with Python 3.12.3 and venv pybind11 before building the binding. Building the test runner and probe with examples enabled hit pinned ns3-ai example compilation errors; the ignored CMake cache was set to `NS3_EXAMPLES=OFF` for these targets and restored to `NS3_EXAMPLES=ON` afterward. The C++ target, three existing unit suites, isolated helper/mobility probe and both Python bridge imports succeeded; no full ib-ORAN scenario run was possible without the CPU Torch wheels.

## Decisions and evidence

- **Recorded decision (researcher, 2026-11-11):** use whole-cell LOS/NLOS comparisons and mobility as the primary setup. This resolves issue #23's scope and position-choice gate. Evidence: the user's instruction in this work session and [RA-PLAN-001](https://github.com/kirolossedra/oran-publication/issues/23).
- **Retrospective inference:** the isolated helper/mobility probe is sufficient for the selected whole-cell helper and basic repeatability checks, but not for channel propagation or random-stream ordering in the full ib-ORAN setup. Missing CPU Torch wheels prevent the scenario-level check in this environment.

## Engineering feasibility verdicts

| Factor | Verdict for the recorded scope | Evidence boundary |
|---|---|---|
| F1 channel | **CONDITIONAL GO** for researcher-selected whole-cell LOS/NLOS; **CONDITIONAL** for selective one-UE blockage; **BLOCKED in the current default** for mobility-driven UMi condition transitions. | All six links returned the selected class in the isolated probe. Full scenario propagation effects remain unverified. Selective Buildings geometry remains unprobed and is outside the selected scope. |
| F2 mobility | **GO** for the pinned random walk as primary motion; **CONDITIONAL** for matched traces in the full scenario. | Source parameters and isolated two-process repeatability verified; full scenario RNG ordering untested. Pinned `ConstantPosition`, `ConstantVelocity` and `Waypoint` models are controlled alternatives, not selected. |
| F3 controls | **GO** for the source-mapped per-UE UL/DL control and grant-construction path; **CONDITIONAL** for real allocation effect. | xApp maximum, dApp requested grant and C++ applied DCI/grant are distinct. A saturated multi-UE pilot is needed to verify intervention effect. |
| F4 traffic | **CONDITIONAL GO** for UE/flow/direction attribution; **BLOCKED** for independent per-UE loads and deterministic unlimited sources in current config. | Localized config/application changes are needed; no loaded pilot was run. |
| F5 packet tails | **BLOCKED** with current retained KPIs; **CONDITIONAL GO** with packet identity/timestamp instrumentation and explicit censoring. | Existing output preserves aggregate mean delay, not per-packet latency tails. |
| F6 environment | **CONDITIONAL GO** for pinned C++ probes; **BLOCKED** for the Python-controlled scenario until the exact CPU Torch pair is available. | Source pins and C++ build are verified; no dependency substitution was made. |

## Final deliverables

- [Source-backed capability matrix](../research/RA-ENG-001-capability-matrix.md) covering F1–F6, updated with observed isolated helper/mobility evidence.
- [Engineering options and researcher gates](../research/RA-ENG-001-technical-options.md).
- [Source-grounded signal path](../architecture/RA-ENG-001-signal-path.md).
- Project navigation and documentation audit updated for this incomplete mission.
- No campaign results or tracked upstream source patches; no claim of full G1 feasibility at runtime or research novelty.
- The 2026-11-12 staged documentation audit covered seven Markdown paths (72,354 bytes total; largest file 22,128 bytes), with no credential-pattern matches, generated files, or upstream source/build paths; Markdown links and staged whitespace checks passed.
- The follow-up official-index retry stage covered three Markdown paths (55,276 bytes total; largest file 22,148 bytes). The files are documentation only; local links and staged whitespace checks passed, and credential/source-tree scans were clean.
- The 2026-11-12 DNS/download/auth follow-up covered four Markdown paths (64,811 bytes total; largest file 22,166 bytes); fifteen local links resolved and staged whitespace, credential, file-type, size and upstream-tree checks passed.
- The push-verification documentation stage covered three Markdown paths (57,806 bytes total; largest file 22,136 bytes); thirteen local links resolved and staged path, credential and whitespace checks passed.
- Staged-set audit passed for 8 Markdown paths (53,002 bytes total; largest file 17,206 bytes): no credential-pattern matches, binary/generated artifacts, simulator source/build tree, or unrelated paths.
- Local audit commit `36d11a44c023ef7ce5e24a8bfc78576516bdc0c0` was created on `main`. Its push failed because Git could not read a GitHub username. GitHub API verified remote `main` remained `39d37ebfca594bb59640477484f0fbb476f998f0`; this documentation is therefore local only. A status comment was added to issue #14.
- Follow-up documentation commit `60a3a23c3336b41b844e664e12922a3fea4067e0` records the restored pins and researcher decisions. Its push attempt failed with the same missing GitHub username; `origin/main` still tracks `39d37ebfca594bb59640477484f0fbb476f998f0`.
- Local probe-documentation commit `cf9dca0` records the six-link and repeated-mobility outputs. Its push attempt failed with the same credential error; GitHub history still showed remote `main` at `39d37ebfca594bb59640477484f0fbb476f998f0`.
- On 2026-11-12, after GitHub device sign-in and credential-helper setup, the ten local RA-ENG-001 commits were pushed as a fast-forward. `git ls-remote origin refs/heads/main` and local `HEAD` both returned `89b5c1bb2116bd8154a6387fdd9ab93164e96acf`; the worktree was clean. This batch includes the previously local audit, restore, and probe commits listed above.

## Unresolved questions and next steps

The source-backed F1–F6 inspection is documented and the researcher selected whole-cell LOS/NLOS with mobility. The original router DNS failure is bypassed for this active session using DNS-over-TLS, but the official PyTorch index and direct CDN connections still time out; Torch remains absent from the venv. Outstanding work is the bounded Python-runner validation in the restored pinned environment, plus grant, traffic, and packet-tail evidence. Continue only within the ordered issue roadmap; do not advance to another engineering issue until the audit's acceptance evidence is complete.

## Documentation completion checklist

- [x] Report and relevant docs updated
- [x] Diagrams updated where applicable
- [x] Probe source and both run logs preserved under ignored `simulator/`; no prior raw output overwritten
- [x] README, mission index, and audit updated
- [x] Paths, claims, parameters, and reproduction commands checked
- [x] Staged file/size/secret/source-tree audit passed
- [x] Local commit created on `main`; remote head checked before and after push attempt
- [x] Push to `main` completed and remote SHA verified as `89b5c1bb2116bd8154a6387fdd9ab93164e96acf`; local `HEAD` matched and worktree was clean
