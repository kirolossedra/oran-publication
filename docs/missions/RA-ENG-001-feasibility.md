# RA-ENG-001 — Source-Verified G1 Feasibility Audit

**Status:** INCOMPLETE (pinned source restored and NR target built; runtime probes and campaign execution remain incomplete). **Date:** 2026-11-11. **GitHub:** [issue #14](https://github.com/kirolossedra/oran-publication/issues/14).

## Research objective and scope

Determine whether the pinned ns-3.48 / 5G-LENA v5.1 / ns3-ai / Orange ib-ORAN stack can support the G1 engineering factors at the required granularity: per-UE LOS/NLOS, repeatable UE movement, six-UE controls and traffic, and packet-level tail latency with actual RAN allocation evidence. Separate source-supported capabilities from capabilities observed in the Mission 1 smoke run. This is a feasibility audit, not a research campaign.

The required source checkout under ignored `simulator/` is not present in the current workspace. This audit therefore used the exact pinned ib-ORAN and ns-3 sources read-only through their public commit URLs and the exact pinned NR v5.1 helper source. It does not claim that the local installation/build is available. Runtime-dependent conclusions remain UNKNOWN until the pinned environment is restored or its existing path is supplied.

## Scientific motivation and hypotheses (human-owned)

The parent G1 question in [RA-GAP-001, issue #12](https://github.com/kirolossedra/oran-publication/issues/12) is a researcher-owned candidate about LOS/NLOS propagation and mobility under competing UL/DL load, scheduling-policy effectiveness, and per-user P95/P99 latency and allocation tradeoffs. Novelty and final hypotheses are not established by this engineering audit. **Researcher decision recorded 2026-11-11:** use whole-cell LOS/NLOS comparisons with mobility as the primary setup.

## Requirements and acceptance criteria

Follow the ordered F1–F6 audit and acceptance criteria in issue #14: establish global versus per-UE channel-condition feasibility; assess mobility and reproducibility; trace xApp/dApp actions to actual MAC grants; inspect per-UE and directional traffic controls; identify valid packet-tail instrumentation and censoring treatment; and report exact pins, dependencies, risks, and the smallest next validation probes. No full traffic system, analysis pipeline, policy comparison, or multi-factor campaign is in scope.

Acceptance evidence will be recorded separately for F1–F6. Claims will be tagged SOURCE-VERIFIED, OBSERVED, INFERRED, or UNKNOWN. The report remains INCOMPLETE if the pinned source or decisive feasibility evidence cannot be inspected.

## Existing architecture and affected components

**SOURCE-VERIFIED:** Mission 1 records a pinned ns-3.48 / NR v5.1 / ns3-ai / ib-ORAN stack, one gNB and six UEs, TDD at 3.5 GHz and 10 MHz, a Python xApp/dApp control path through ns3-ai shared memory, and an upstream toy-workload smoke run. The existing architecture map is [executed-baseline.md](../architecture/executed-baseline.md); source revisions are in [environment.json](../../manifests/environment.json). This audit checked the exact pinned source code for ib-ORAN and ns-3 plus the NR v5.1 channel helper.

**OBSERVED in this workspace:** repository branch is `main`, two local documentation commits ahead of `origin/main` at `39d37ebfca594bb59640477484f0fbb476f998f0`; the expected ignored `simulator/` directory was initially absent. Host is Ubuntu 24.04.4 x86_64, 20 logical CPUs, 30 GiB RAM (24 GiB available), 510 GiB free workspace filesystem before restoration, system Python 3.14.3, Python 3.12.3 at `/usr/bin/python3.12`, GCC 13.3.0, CMake 3.28.3, Ninja, and Conda. Docker CLI 29.4.1 is installed but access to `/var/run/docker.sock` is denied; Podman is absent; `/dev/kvm` is absent; `ip` cannot open a netlink socket in this execution environment.

Target source areas from issue #14 were inspected as documented in the [capability matrix](../research/RA-ENG-001-capability-matrix.md), [technical options](../research/RA-ENG-001-technical-options.md), and [signal-path diagram](../architecture/RA-ENG-001-signal-path.md): ib-ORAN NR environment/common setup, pinned NR channel helper, ns-3 condition and propagation models, orchestrator/Python schedulers, NR MAC scheduler/shared-memory interfaces, per-UE app setup, FlowMonitor aggregation/cleanup, and application packet handling.

## Implementation details and alternatives

No upstream simulator source was modified. The exact pinned source audit establishes: helper-level global forced LOS/NLOS is directly supported; selective link conditions are a small, unproven Buildings-geometry probe; default 3GPP condition and channel updates are disabled at period zero; and per-UE mobility, traffic, control and measurement paths have the limits recorded in the matrix. The researcher approved the whole-cell LOS/NLOS and mobility scope, resolving the scope gate. No different simulator, custom channel model, or copied legacy NR-U patch was used.

## Architecture/algorithm/workflow diagrams

See [RA-ENG-001 signal path](../architecture/RA-ENG-001-signal-path.md). Solid arrows are source-traced; dashed edges are proposed diagnostics, not implemented functionality.

## Changed files and reproducible patches

Documentation-only changes: this report, the capability matrix, technical options, source-grounded signal-path diagram, root README navigation, docs navigation, mission index, and documentation audit. No source/configuration patch has been made.

## Dependencies, versions, configuration, seeds, commands

Expected pins are documented in `manifests/environment.json`; exact upstream source refs are listed in the capability matrix. Sources were downloaded under the ignored `simulator/` path and checked out at ns-3 `d2add90b452d600cfb4859baed8e9ea633519447`, NR `cedceadda17392c90587fb9400eb9b1f8c236713`, ns3-ai `b8c9858294b1d6a7f122b5154a3ce25057a54740`, and ib-ORAN `3ea5046389f0eb993cdf01ef6d6d33017e6921bb`; `git rev-parse HEAD` matched each pin. The C++ prefix was restored from `manifests/cpp-environment-lock.txt`. Python 3.12.3 venv packages were installed from the frozen lock without dependency re-resolution, excluding `torch==2.9.1+cpu` and `torchvision==0.24.1+cpu`; DNS resolution failed for both the official PyTorch CPU index and its alternate download CDN. The exact wheels are listed by the [official Torch CPU index](https://download.pytorch.org/whl/cpu/) and [official torchvision CPU index](https://download.pytorch.org/whl/cpu/torchvision/). The failed direct-wheel attempt is logged in `simulator/logs/RA-ENG-001-restore-20261111/torch-cpu-wheel-download.log`. The missing Torch pair is an environment limitation, not a substitution. Configure commands used CMake with explicit Python 3.12 include/library paths and the venv's pybind11 3.1.0. Build commands: `./ns3 configure --enable-examples --enable-tests`; `./ns3 build ns3iboran_nr -j 4`; `ninja -C cmake-cache -j 4 proto-objects`; and `ninja -C cmake-cache -j 4 iboran_shm_structure_py_binding`. A local ccache directory/config under ignored `simulator/tooling/` was needed because the host ccache default config path is read-only. Docker daemon access and netlink inspection failed with permission errors; KVM and Podman were absent.

## Tests and verification evidence (logs/paths)

**Observed build and unit-test verification:** the pinned `ns3iboran_nr` target completed successfully (1,035/1,035 Ninja steps); protobuf objects built (3/3); `iboran_shm_structure_py_binding` built (1,082/1,082 steps); and `from ns3ai_utils import Experiment` plus `import iboran_shm_structure_py_binding` succeeded in the Python 3.12.3 venv with the local C++ library path. The existing ns-3 suites `nr-channel-setup-test`, `mobility-trace`, and `three-gpp-propagation-loss-model` passed (0.013 s, 0.006 s, and 2.639 s). These verify helper factory selection, the existing mobility-trace test, and the pinned propagation-loss test suite; they do not test all six ib-ORAN links or repeat the scenario's six UE traces across runs. The first binding configure selected host Python 3.14 and the system pybind11; CMake was then reconfigured with explicit Python 3.12 paths and venv pybind11 3.1.0 before the successful binding build. The first build attempt failed because ccache tried to write under read-only `/home/george/.config`; subsequent builds used the ignored project-local ccache path. Building the test runner with examples enabled encountered an unrelated pinned ns3-ai example error (`burst-sink.h` uses `std::map` without including `<map>`). The ignored CMake build cache was temporarily configured with examples disabled to build and run the test runner, then restored to the documented examples-enabled configuration; no upstream source file was patched. Reproducibility outputs (source pins, explicit C++ package list, Python freeze, import result, build/test logs, and CPU-wheel download failure) are under the unique ignored path `simulator/logs/RA-ENG-001-restore-20261111/`. No ib-ORAN scenario or campaign was run. Whole-cell condition behavior across all six scenario links, same-seed mobility repeatability in that scenario, actual grant/traffic observations, and packet-level tail measurement remain unverified. Both the official PyTorch CPU index and alternate download CDN failed DNS resolution, so the pinned CPU Torch wheels could not be retrieved.

## Raw data and result references

No raw data or simulator runs were created. If an authorized diagnostic becomes necessary, it will use a unique run ID and remain in the ignored simulator tree; no prior evidence will be overwritten.

## Analysis, sample sizes, uncertainty, interpretation

Not applicable to the source audit. No performance result or statistical claim is made.

## Limitations and unverified assumptions

- The pinned source and C++ build are now present under ignored `simulator/`; the exact CPU Torch and torchvision packages remain unavailable, so the complete Python runtime and campaign have not been validated.
- Host tool presence does not establish runtime behavior or container access. This session cannot connect to Docker, inspect network interfaces/routes through netlink, or use KVM/Podman.
- Mission 1 claims are recorded documentation evidence until reconciled with the manifest and any preserved local evidence available here.
- No LOS/NLOS, mobility, grant, traffic, or packet-tail capability is yet independently verified in source during this mission.

## Problems, failures, and resolutions

Initial obstacle: expected ignored simulator tree absent. Downloaded all four exact pinned repositories and restored the locked C++ dependencies and the available Python lock packages. The initial pip resolution selected CUDA-enabled Torch through an unpinned transitive dependency; it was stopped before CUDA packages installed. Installing the committed CPU Torch pair separately failed because both the official PyTorch CPU index and its alternate download CDN did not resolve. The exact Linux/Python 3.12 CPU wheel files are listed on the official index pages, but no substitute was installed. Build first failed on the host's read-only ccache config and used the local ignored cache on retry. Initial CMake selected Python 3.14 for ib-ORAN; it was reconfigured with Python 3.12.3 and venv pybind11 before building the binding. Building test runner with examples enabled failed on the upstream ns3-ai example's missing `<map>` include; the ignored CMake cache was set to `NS3_EXAMPLES=OFF` for the unit suites and restored to `NS3_EXAMPLES=ON` afterward. The C++ target, three existing unit suites and both Python bridge imports succeeded; no ib-ORAN scenario run was possible without the CPU Torch wheels.

## Decisions and evidence

- **Recorded decision (researcher, 2026-11-11):** use whole-cell LOS/NLOS comparisons and mobility as the primary setup. This resolves issue #23's scope and position-choice gate. Evidence: the user's instruction in this work session and [RA-PLAN-001](https://github.com/kirolossedra/oran-publication/issues/23).
- **Retrospective inference:** because `simulator/` is absent, read-only pinned-source inspection is the least invasive way to continue this audit without changing the environment.

## Final deliverables

- [Source-backed capability matrix](../research/RA-ENG-001-capability-matrix.md) covering F1–F6.
- [Engineering options and researcher gates](../research/RA-ENG-001-technical-options.md).
- [Source-grounded signal path](../architecture/RA-ENG-001-signal-path.md).
- Project navigation and documentation audit updated for this incomplete mission.
- No experiment results or source patches; no claim of G1 feasibility at runtime or research novelty.
- Staged-set audit passed for 8 Markdown paths (53,002 bytes total; largest file 17,206 bytes): no credential-pattern matches, binary/generated artifacts, simulator source/build tree, or unrelated paths.
- Local audit commit `36d11a44c023ef7ce5e24a8bfc78576516bdc0c0` was created on `main`. Its push failed because Git could not read a GitHub username. GitHub API verified remote `main` remained `39d37ebfca594bb59640477484f0fbb476f998f0`; this documentation is therefore local only. A status comment was added to issue #14.
- Follow-up documentation commit `60a3a23c3336b41b844e664e12922a3fea4067e0` records the restored pins and researcher decisions. Its push attempt failed with the same missing GitHub username; `origin/main` still tracks `39d37ebfca594bb59640477484f0fbb476f998f0`.

## Unresolved questions and next steps

The source-backed F1–F6 inspection is documented and the researcher selected whole-cell LOS/NLOS with mobility. Outstanding work is the bounded runtime validation in the restored pinned environment, which requires the missing CPU Torch wheels for the Python-controlled runner, and the remaining grant, traffic, and latency evidence. Continue only within the ordered issue roadmap; the next engineering issue remains gated on completing this audit's acceptance evidence.

## Documentation completion checklist

- [x] Report and relevant docs updated
- [x] Diagrams updated where applicable
- [x] Results/logs/config/patches preserved (none created; no raw run overwritten)
- [x] README, mission index, and audit updated
- [x] Paths, claims, parameters, and reproduction commands checked
- [x] Staged file/size/secret/source-tree audit passed
- [x] Local commit created on `main`; remote head checked before and after push attempt
- [ ] Push to `main` completed and remote SHA matches local (blocked: GitHub username unavailable to Git)
