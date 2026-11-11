# RA-ENG-001 — Source-Verified G1 Feasibility Audit

**Status:** INCOMPLETE (source audit documented; local runtime probes unavailable). **Date:** 2026-11-11. **GitHub:** [issue #14](https://github.com/kirolossedra/oran-publication/issues/14).

## Research objective and scope

Determine whether the pinned ns-3.48 / 5G-LENA v5.1 / ns3-ai / Orange ib-ORAN stack can support the G1 engineering factors at the required granularity: per-UE LOS/NLOS, repeatable UE movement, six-UE controls and traffic, and packet-level tail latency with actual RAN allocation evidence. Separate source-supported capabilities from capabilities observed in the Mission 1 smoke run. This is a feasibility audit, not a research campaign.

The required source checkout under ignored `simulator/` is not present in the current workspace. This audit therefore used the exact pinned ib-ORAN and ns-3 sources read-only through their public commit URLs and the exact pinned NR v5.1 helper source. It does not claim that the local installation/build is available. Runtime-dependent conclusions remain UNKNOWN until the pinned environment is restored or its existing path is supplied.

## Scientific motivation and hypotheses (human-owned)

The parent G1 question in [RA-GAP-001, issue #12](https://github.com/kirolossedra/oran-publication/issues/12) is a researcher-owned candidate about LOS/NLOS propagation and mobility under competing UL/DL load, scheduling-policy effectiveness, and per-user P95/P99 latency and allocation tradeoffs. Novelty and final hypotheses are not established by this engineering audit. A whole-cell channel intervention cannot be substituted for a single-UE intervention without researcher approval.

## Requirements and acceptance criteria

Follow the ordered F1–F6 audit and acceptance criteria in issue #14: establish global versus per-UE channel-condition feasibility; assess mobility and reproducibility; trace xApp/dApp actions to actual MAC grants; inspect per-UE and directional traffic controls; identify valid packet-tail instrumentation and censoring treatment; and report exact pins, dependencies, risks, and the smallest next validation probes. No full traffic system, analysis pipeline, policy comparison, or multi-factor campaign is in scope.

Acceptance evidence will be recorded separately for F1–F6. Claims will be tagged SOURCE-VERIFIED, OBSERVED, INFERRED, or UNKNOWN. The report remains INCOMPLETE if the pinned source or decisive feasibility evidence cannot be inspected.

## Existing architecture and affected components

**SOURCE-VERIFIED:** Mission 1 records a pinned ns-3.48 / NR v5.1 / ns3-ai / ib-ORAN stack, one gNB and six UEs, TDD at 3.5 GHz and 10 MHz, a Python xApp/dApp control path through ns3-ai shared memory, and an upstream toy-workload smoke run. The existing architecture map is [executed-baseline.md](../architecture/executed-baseline.md); source revisions are in [environment.json](../../manifests/environment.json). This audit checked the exact pinned source code for ib-ORAN and ns-3 plus the NR v5.1 channel helper.

**OBSERVED in this workspace:** repository branch is `main`, initially clean and aligned with `origin/main` at `39d37ebfca594bb59640477484f0fbb476f998f0`; the expected ignored `simulator/` directory is absent. Host is Ubuntu 24.04.4 x86_64, 20 logical CPUs, 30 GiB RAM (24 GiB available), 512 GiB free workspace filesystem, system Python 3.14.3, GCC 13.3.0, CMake 3.28.3, Ninja, and Conda. Docker CLI 29.4.1 is installed but access to `/var/run/docker.sock` is denied; Podman is absent; `/dev/kvm` is absent; `ip` cannot open a netlink socket in this execution environment. These host facts do not establish that the pinned simulator environment exists or can be restored here.

Target source areas from issue #14 were inspected as documented in the [capability matrix](../research/RA-ENG-001-capability-matrix.md), [technical options](../research/RA-ENG-001-technical-options.md), and [signal-path diagram](../architecture/RA-ENG-001-signal-path.md): ib-ORAN NR environment/common setup, pinned NR channel helper, ns-3 condition and propagation models, orchestrator/Python schedulers, NR MAC scheduler/shared-memory interfaces, per-UE app setup, FlowMonitor aggregation/cleanup, and application packet handling.

## Implementation details and alternatives

No implementation or simulator modification was made. The exact pinned source audit establishes: helper-level global forced LOS/NLOS is directly supported; selective link conditions are a small, unproven Buildings-geometry probe; default 3GPP condition and channel updates are disabled at period zero; and per-UE mobility, traffic, control and measurement paths have the limits recorded in the matrix. A different simulator, channel model, global-for-per-UE substitution, or copied legacy NR-U patch remains out of scope.

## Architecture/algorithm/workflow diagrams

See [RA-ENG-001 signal path](../architecture/RA-ENG-001-signal-path.md). Solid arrows are source-traced; dashed edges are proposed diagnostics, not implemented functionality.

## Changed files and reproducible patches

Documentation-only changes: this report, the capability matrix, technical options, source-grounded signal-path diagram, root README navigation, docs navigation, mission index, and documentation audit. No source/configuration patch has been made.

## Dependencies, versions, configuration, seeds, commands

Expected pins are documented in `manifests/environment.json`; exact upstream source refs are listed in the capability matrix. No experiment seed or effective configuration applies to this source audit. Initial environment commands: `uname -a`, `cat /etc/os-release`, `nproc`, `free -h`, `python --version`, `command -v gcc g++ cmake ninja conda docker podman git`, `df -h .`, `git status --short --branch`, `docker version --format '{{.Client.Version}}'`, `docker info --format '{{.ServerVersion}}'`, `ip -brief link`, `ip route`, and `/dev/kvm`/Podman presence checks. Docker daemon access and netlink inspection failed with permission errors; KVM and Podman were absent.

## Tests and verification evidence (logs/paths)

No tests or experiments ran. Source inspection evidence is linked line-by-line in the capability matrix and diagram. F1's one-UE Buildings geometry check, F2 paired trajectory repeatability, local pin/build verification, and runtime grant/traffic observations remain unverified because the local simulator tree is missing. Initial host and Git evidence is recorded above.

## Raw data and result references

No raw data or simulator runs were created. If an authorized diagnostic becomes necessary, it will use a unique run ID and remain in the ignored simulator tree; no prior evidence will be overwritten.

## Analysis, sample sizes, uncertainty, interpretation

Not applicable to the source audit. No performance result or statistical claim is made.

## Limitations and unverified assumptions

- The local pinned simulator source/build/environment is not present at the expected `simulator/` path.
- Host tool presence does not establish usable dependencies, channel configuration, runtime behavior, or container access. This session cannot connect to Docker, inspect network interfaces/routes through netlink, or use KVM/Podman.
- Mission 1 claims are recorded documentation evidence until reconciled with the manifest and any preserved local evidence available here.
- No LOS/NLOS, mobility, grant, traffic, or packet-tail capability is yet independently verified in source during this mission.

## Problems, failures, and resolutions

Initial obstacle: expected ignored simulator tree absent. Exact pinned source inspection resolved source-level questions without reinstalling or cloning. Local runtime/build and bounded probes remain blocked by the absent environment; no replacement was downloaded.

## Decisions and evidence

- **Recorded decision (issue #14 and issue #23):** investigate selective UE-link LOS/NLOS first; stop for the researcher’s scope decision before implementing radio/motion controls. Evidence: [RA-ENG-001](https://github.com/kirolossedra/oran-publication/issues/14), [RA-PLAN-001](https://github.com/kirolossedra/oran-publication/issues/23).
- **Retrospective inference:** because `simulator/` is absent, read-only pinned-source inspection is the least invasive way to continue this audit without changing the environment.

## Final deliverables

- [Source-backed capability matrix](../research/RA-ENG-001-capability-matrix.md) covering F1–F6.
- [Engineering options and researcher gates](../research/RA-ENG-001-technical-options.md).
- [Source-grounded signal path](../architecture/RA-ENG-001-signal-path.md).
- Project navigation and documentation audit updated for this incomplete mission.
- No experiment results or source patches; no claim of G1 feasibility at runtime or research novelty.
- Staged-set audit passed for 8 Markdown paths (53,002 bytes total; largest file 17,206 bytes): no credential-pattern matches, binary/generated artifacts, simulator source/build tree, or unrelated paths.

## Unresolved questions and next steps

The source-backed F1–F6 inspection is documented. The outstanding work is runtime validation in the pinned local environment and researcher decisions on selective single-UE versus whole-cell channel treatment and primary mobility versus fixed positions. Do not advance to RA-ENG-002 or later missions until those gates are resolved.

## Documentation completion checklist

- [x] Report and relevant docs updated
- [x] Diagrams updated where applicable
- [x] Results/logs/config/patches preserved (none created; no raw run overwritten)
- [x] README, mission index, and audit updated
- [x] Paths, claims, parameters, and reproduction commands checked
- [x] Staged file/size/secret/source-tree audit passed
- [ ] Commit created and pushed to `main`; remote SHA verified
