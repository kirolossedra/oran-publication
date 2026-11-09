# Mission 1 — Install, build, and validate the 5G ib-ORAN baseline

**Status:** COMPLETE. **Date:** 2026-11-09. **Branch:** main.

**Scope:** environment installation and one upstream baseline only.

## Objective and scientific motivation

Establish the selected, reproducible ns-3/5G-LENA/ib-ORAN environment, compile its NR scenario and Python bridge, and run one upstream NR workload with execution evidence. This is infrastructure validation, not an experiment about the proposed latency-sensitive UE and background-load scenario. The human researcher retains ownership of research hypotheses and interpretation.

## Requirements and acceptance criteria

The accepted stack had to use the revisions in manifests/environment.json, build ns3iboran_nr, import the Python bridge, complete an upstream NR simulation, produce and preserve KPI outputs, and provide source/runtime evidence for the xApp/dApp control path. Python 3.11+ was required; the existing Python 3.12.3 was not to be replaced absent incompatibility. Keep simulator sources/build and outputs isolated under ignored simulator/, do not use NR-U sources/patches, preserve main and prior files, avoid unrelated system package changes, and stop before custom traffic, mobility or policy work.

## Existing architecture and affected components

The upstream stack is ns-3.48 with 5G-LENA NR v5.1, ns3-ai shared-memory C++/Python integration and Orange ib-ORAN. Exact executed paths and future source modification locations are in [the architecture map](../architecture/executed-baseline.md). No upstream source file was modified in this mission.

## Environment audit and selected revisions

Host before installation: Python 3.12.3, GCC 13.3.0, CMake 3.28.3, 22 logical CPUs, about 9 GiB available RAM of 15 GiB, and 20 GiB free disk. Existing system Boost was 1.83 and pybind11-dev was 2.11.1; Protobuf C++ development/compiler were not found, below the ib-ORAN guide's required versions. yaml-cpp 0.8 was present. After install/build/run, about 13 GiB disk remained. No system apt package changes were made.

| Component | Tag/ref | Pinned source commit | Verification |
|---|---|---|---|
| ns-3 | ns-3.48 | d2add90b452d600cfb4859baed8e9ea633519447 | Exact tag; annotated tag object 422ef9dc12d9bcd4ee8f4b1374dffcc029a3675c |
| 5G-LENA NR | v5.1 | cedceadda17392c90587fb9400eb9b1f8c236713 | Exact tag; annotated tag object 2fab8d9b8b5f823ab8a83495e4239b246182071b |
| ns3-ai | main snapshot | b8c9858294b1d6a7f122b5154a3ce25057a54740 | Exact checkout |
| Orange ib-ORAN | main snapshot | 3ea5046389f0eb993cdf01ef6d6d33017e6921bb | Exact checkout |

The first source validation compared ns-3 HEAD to the annotated tag-object hash rather than its peeled commit and falsely indicated a mismatch. \`git rev-parse ns-3.48^{}\` resolved the actual source commit; source itself was correct. The manifest now records tag-object and peeled commit separately. No historical ns-3.35/NR v1.2/NR-U source or patch was used.

## Dependencies, installation and build decisions

Newer C++ requirements were placed in local micromamba prefix simulator/envs/cpp: Boost 1.89.0, Protobuf 6.33.5/protoc 33.5, yaml-cpp 0.8. pybind11 3.1.0 and Python dependencies were installed in simulator/ns-3.48/.venv. CPU Torch 2.9.1+cpu and torchvision 0.24.1+cpu were used. The upstream requirements leave Torch broadly unpinned; the initial pip resolution began selecting CUDA-enabled Torch and several gigabytes of NVIDIA libraries. It was stopped before installing Torch/CUDA, and the CPU build was selected because this installation baseline has no GPU requirement. The diagnostic note and successful package logs are preserved locally. Python 3.12.3 satisfies the documented minimum, so Python 3.11 was not installed.

The upstream quick setup was inspected. It would check system-only Boost locations, pip install broad requirements, register an iboran.pth, build and offer an interactive run. Those steps were implemented explicitly in local paths to retain dependency isolation. The ns3-ai examples were not built because the ib-ORAN guide says they do not build with ns-3.48 and ib-ORAN does not need them.

Configure command recorded in simulator/logs/ns3-configure.log used the ns-3 wrapper with examples/tests enabled, C++ prefix path and project venv Python/pybind11. The effective CMake invocation was:

    cmake -S <simulator>/ns-3.48 -B <simulator>/ns-3.48/cmake-cache \
      -DCMAKE_BUILD_TYPE=default -DNS3_ASSERT=ON -DNS3_LOG=ON \
      -DNS3_WARNINGS_AS_ERRORS=OFF -DNS3_NATIVE_OPTIMIZATIONS=OFF \
      -DNS3_EXAMPLES=ON -DNS3_TESTS=ON -G Ninja --warn-uninitialized

The build and bridge commands were run from the ns-3 source root:

    ./ns3 build ns3iboran_nr -j 2
    ninja -C cmake-cache -j2 proto-objects
    ninja -C cmake-cache -j2 iboran_shm_structure_py_binding

The NR executable built successfully at 1086/1086 steps. ns-3's wrapper did not expose the binding as a known target; the existing generated Ninja target was therefore invoked directly. Generated protobuf headers had to be built first. Python imports for the generated ib-ORAN module and ns3ai_utils.Experiment succeeded. Build/config logs are under simulator/logs/. Nonfatal upstream warnings: signed/unsigned comparison in ib-ORAN code and extra semicolon in an ns3-ai header. No protocol/code change was made to silence them. A diagnostic CMake package probe run without enabling a language emitted a Protobuf complaint; actual CMake configure found local Protobuf correctly, and compilation plus runtime succeeded.

## Baseline scenario and exact configuration

Unique run ID: 20261109-nr-toy-ibTopKCqi-k3-seed5. The command was executed from contrib/iboran/model/iboran_campaign with the local Python environment and library search path active:

    python3 iboran_run.py --rat_type=NR --k=3 --dapp_algo_ue_selection=ibTopKCqi --rng_run=5 --save_dapp_log=true

It exited 0. Effective settings from the saved config:

| Parameter | Value |
|---|---|
| RAT/topology | NR; 1 gNB, 6 UEs, 1 remote host |
| Area / duration | 500 m square parameter; 20 simulated seconds |
| UE motion | Source installs RandomWalk2dMobilityModel; speed 0.83 m/s and turn-distance 100 m; random initial positions. No fixed-position control was applied. |
| NR carrier | 3.5 GHz, 10 MHz, 1 CC, 1 BWP, numerology 1 |
| TDD pattern | DL\|DL\|DL\|DL\|F\|UL\|UL\|UL\|UL\|F\| |
| Antennas | gNB 4x4; UE 2x2 |
| Baseline UDP downlink | Enabled; 512-byte packets; configured 2,000,000 bit/s |
| Baseline UDP uplink | Enabled; 512-byte packets; configured 1,000,000 bit/s |
| Backhaul | 100 Gbps; MTU 1500 B; configured delay 10 ms |
| dApp | k=3, ibTopKCqi, 1-subframe control period |
| xApp | Bypass RBG-bounding algorithm, 1-frame control period |
| Dataset workload | Bundled toy dataset; EMBEDDING; CLIP; object ID range 4–5 |
| Randomization | rngRun=5 |
| Logs | verbose; dApp decision log saved |

The application also exchanges image/embedding payloads. The ten-image bundled toy set has ten 36,342-byte PNG files. The CLIP checkpoint was downloaded to the ignored local upstream model cache and loaded. No Market-1501 data were downloaded. The workload is upstream image/embedding traffic; it is not industrial-robot traffic and should not be interpreted as the future proposed latency-sensitive workload.

## Execution results and control verification

**Observed process evidence:** execution log reports shared-memory interfaces established, xApp/dApp schedulers initialized, simulation finished, and scheduling terminated. Exit marker says status 0. NR binary ran through the orchestrator, not merely a Python import or application startup.

**Observed control execution:** xApp reports 22,337 control steps, 1,887 decisions, zero errors. dApp reports 22,337 control steps, 7,548 decisions, zero errors. Saved dApp trace has 7,588 lines, including its header and 7,586 records with RNTI fields. Records include per-RNTI PRB ranges and MCS. This directly demonstrates dApp scheduling decisions. Source shows the orchestrator receives C++ reports, calls each Python scheduler, and sends messages back through ns3-ai. NR MAC source consumes per-UE max RBG values and applies them during UL/DL grants.

**xApp interpretation:** the configured xApp algorithm was Bypass. The xApp loop executed and generated decisions, but Bypass does not establish that restrictive or optimized resource bounds were imposed. Source includes algorithms that set RBG bounds; this mission did not run a second policy or implement one. We therefore confirm control integration and dApp allocations, not a nontrivial xApp allocation-policy effect or external RIC interoperability.

### KPI values directly observed

The saved KPI JSON uses link key 0 for downlink and 1 for uplink in this run, consistent with the execution summary.

| KPI | Downlink | Uplink | Meaning/caveat |
|---|---:|---:|---|
| Average PDR | 100.00% | 95.8333% | Rx/Tx at flow aggregate. |
| Total throughput | 2588.12 kbps | 1587.98 kbps | Sum of per-flow throughput outputs for link. |
| Average throughput | 431.353 kbps | 264.664 kbps | Link total divided across six per-UE flows. |
| Average latency | 25.0503 ms | 30.9464 ms | FlowMonitor aggregate delay sum / received packets, aggregated by link. |
| Average jitter | 1.89584 ms | 7.49607 ms | FlowMonitor jitter sum / (received packets - 1), aggregated by link. |
| dApp decision time | 0.221625 ms | 0.147095 ms | Mean Python dApp decision time. |
| xApp decision time | 0.115447 ms | 0.048253 ms | Mean Python xApp decision time. |
| RBG usage KPI | 76.6667% | 11.7738% | Upstream name says PRBUtilizationRatio; implementation uses RBGs allocated by dApp / RBGs offered at dApp decision steps, not independent PHY utilization. |

The standard FlowMonitor portion has 16 UDP flows, 72 transmitted packets and 71 received packets. One uplink flow received 3 of 4; the remaining listed flows received all packets. These flow-monitor totals do not imply the image/embedding application has the same packet denominator. Exact copied KPI JSON and effective config are committed under results/mission1-nr-baseline/. Hashes for those and the local full execution/dApp logs are listed in source-artifact-sha256.txt.

## Measurement definitions and limits

Upstream flow computation in iboran_orchestrator.py derives PDR as rxPackets/txPackets, throughput from rxBytes over timeLastRxPacket minus timeFirstTxPacket, latency as delaySum/rxPackets, and jitter as jitterSum/(rxPackets-1). Link summary averages measurements over the corresponding flows/UEs. Internal decision time measures Python scheduler processing; PRBUtilizationRatio is specifically a dApp-side RBG-allocation fraction according to upstream docs/source.

The results are a one-run smoke check of a short, small-packet-count workload and do not characterize stable performance. KPI JSON provides aggregate means, not packet-level records. No P95/P99 can be calculated from those aggregates. FlowMonitor XML is written under a temporary hidden .flowstats path; successful runner cleanup deletes it after extracting KPI values. Per-packet latency and retransmission-level accounting require future instrumentation or preserving/parsing packet-level traces before cleanup.

## Failures and troubleshooting

- **Tag SHA mismatch:** initial check compared annotated tag-object ID to commit. Verified peeled commit; no source replacement was necessary.
- **System dependency shortfall:** avoided system-wide upgrades using project-local micromamba prefix and venv.
- **Torch/CUDA resolution:** cancelled broad pip resolution before Torch/CUDA installation and selected CPU-only wheels; no GPU package installed.
- **Python binding target:** ns-3 build wrapper did not list the target. Used generated Ninja target and first built Protobuf objects; import then succeeded.
- **Build diagnostics:** nonfatal upstream warnings preserved in logs; warnings-as-errors remained off. No implementation behavior or upstream code was modified.
- **FlowMonitor XML retention:** upstream cleanup removed it by design after KPI analysis; run was not modified after completion to fabricate/restore data.

## Decisions and evidence

| ID | Decision | Rationale/evidence type |
|---|---|---|
| M1-DR-01 | Keep C++/Python dependencies project-local | Host libraries missed upstream floors; isolated prefix and venv avoid unintended host changes. |
| M1-DR-02 | Use CPU Torch | No GPU requirement in baseline; upstream requirements were unpinned and pip began selecting CUDA dependencies. |
| M1-DR-03 | Run upstream toy workload with Bypass xApp | Uses supported example to validate control plumbing without introducing a research policy; verifies invocation, not restrictive resource allocation. |
| M1-DR-04 | Retain full run locally; publish compact KPI/config | Full artifacts are large and ignored; a small reviewable subset can be published while full local logs remain intact. |

Stack selection is covered by [D-001](../decisions/D-001-tested-stack.md); project isolation and research scope by D-002 and D-003. New records M1-DR-01 through M1-DR-04 are retrospective rationales grounded in observed constraints and source evidence, not claims that an original decision log existed at installation time.

## Evidence, reproduction and deliverables

Full local build/install logs: simulator/logs/ (ignored). Full local run: simulator/runs/20261109-nr-toy-ibTopKCqi-k3-seed5/ (ignored; includes default/effective config, full execution.log, exit-status.txt, KPI JSON, dApp trace, NetAnim XML and recovered outputs). Compact committed evidence: results/mission1-nr-baseline/.

Reproduction steps and command are in [installation documentation](../INSTALLATION.md). Exact commits and dependency versions are in [manifest](../../manifests/environment.json), with complete Python package pins in [the Python lock](../../manifests/python-environment-lock.txt) and Linux C++ artifact pins in [the C++ lock](../../manifests/cpp-environment-lock.txt). The run is tied to RNG run 5 and the effective YAML copy. Build is incremental and successful. No custom scenario or algorithm was implemented.

## Limitations and unresolved items

1. No P95/P99/P99.9 support in this baseline output; add per-packet timestamps/records or preserve and parse a suitable trace.
2. The user's latency-sensitive/background load scenario is not implemented; standard bit-rate defaults and image/embedding workload cannot answer that question.
3. The xApp Bypass run verifies invocation, not constrained resource bounds. A future baseline comparison should select an existing nontrivial upstream algorithm or document why a different control setting is used.
4. PRBUtilizationRatio is a scheduler-side RBG count ratio, not a generic air-interface occupancy measure.
5. FlowMonitor XML is removed by normal cleanup; future raw-packet work needs a documented preservation mechanism.
6. One smoke run is not statistically established; no causal claims, confidence intervals, focused mobility analysis, standards conformance, external RIC interoperability, or real-world deployment claims are made. UEs do use the upstream RandomWalk2d model in this run, so it should not be treated as a fixed-topology reference.
7. The upstream CLIP checkpoint is cached locally but not committed; fresh hosts may need model access/download.

## Completion checklist

- [x] Report created before installation and completed with source/config/run details
- [x] Exact source tags/commits and dependencies recorded
- [x] Build completed and logs preserved
- [x] Python binding/import verified
- [x] Upstream NR run completed, exit status preserved, KPI files inspected
- [x] Source-supported and observed control behavior distinguished
- [x] Workload, measurements, limitations and implementation map documented
- [x] Mermaid architecture and topology diagrams included
- [x] README, compatibility/install docs, mission index and audit updated
- [x] Reproduction commands, parameters, seed and results linked
- [x] Staged-content audit passed; mission commit `ed4d272be7e04f61083b1e748a7846bf20a6746a` was pushed to `main` and matched `git ls-remote` at publication time
