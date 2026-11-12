# O-RAN Based 5G RAN Performance and Resource Allocation

This independent research project uses a separately pinned ns-3/5G-LENA/ib-ORAN environment to study RAN scheduling, latency, throughput, reliability, and resource allocation. The historical [NR-U/Wi-Fi project](https://github.com/kirolossedra/nru-publication) remains an archive; no legacy source, libraries, or patches are reused here.

## Research question and motivation

How do baseline and modified RAN resource-allocation policies affect a latency-sensitive UE and competing UEs as background uplink and downlink traffic increases? A 5G RAN has finite radio resources that its scheduler allocates among UEs with different channel and traffic conditions. The work emphasizes wireless-system modeling and controlled simulation, rather than constructing an elaborate external RIC.

The intended first research scenario has one gNB, one latency-sensitive UE, and several background UEs. Planned outcomes include mean/P95/P99 packet latency, UL/DL throughput, packet loss, PRB use, and the effect on competing UEs. Offered traffic, delivered traffic, and radio allocation will be reported separately. Mobility is optional and requires validation before use.

## Current state

Mission 1 installed and built the pinned upstream stack and completed one upstream NR toy-workload smoke baseline. The run establishes environment and control-loop operation only. It is **not** the proposed latency-under-load experiment: upstream workload sends/receives image/embedding payloads, the run is a single seed, and standard outputs expose aggregate mean latency rather than packet-level tail latency. No research allocation policy or custom load scenario has been implemented.

The tested baseline is ns-3.48 + 5G-LENA NR v5.1 + ns3-ai + Orange ib-ORAN, with Python 3.12.3. Exact source commits, local dependency versions, and run identity are in [the environment manifest](manifests/environment.json), with [Python package pins](manifests/python-environment-lock.txt) and a [linux-64 C++ package lock](manifests/cpp-environment-lock.txt). Source trees, virtual environment, build products, model cache, full logs, and run directories stay in ignored `simulator/`.

## Architecture

The actual executed control path is diagrammed in [the runtime architecture report](docs/architecture/executed-baseline.md). The planned research topology and methodology remain documented separately. In this baseline, ns-3 runs NR radio/network events; 5G-LENA provides NR gNB/UE and MAC scheduling; ib-ORAN C++ agents communicate over the ns3-ai shared-memory interface with Python xApp/dApp schedulers; KPI and payload outputs are collected by the upstream runner.

## Documentation index

- [Compatibility and exact pins](docs/COMPATIBILITY.md)
- [Installation and reproducibility record](docs/INSTALLATION.md)
- [Executed baseline architecture and source map](docs/architecture/executed-baseline.md)
- [Architecture and control boundary](docs/architecture/simulator-and-control.md)
- [Initial research scenario](docs/architecture/initial-scenario.md)
- [Proposed study methodology](docs/methodology/proposed-study.md)
- [Mission history](docs/MISSIONS.md)
- [Mission 1 installation report](docs/missions/mission-1-installation.md)
- [RA-ENG-001 feasibility audit](docs/missions/RA-ENG-001-feasibility.md) · [capability matrix](docs/research/RA-ENG-001-capability-matrix.md) · [technical options](docs/research/RA-ENG-001-technical-options.md)
- [RA-ENG-001 signal-path diagram](docs/architecture/RA-ENG-001-signal-path.md)
- [Decision records](docs/decisions/README.md)
- [Documentation audit](docs/DOCUMENTATION-AUDIT.md)
- [Governance](AGENTS.md) · [mission template](templates/MISSION-TEMPLATE.md)

## Next step

The source-level RA-ENG-001 audit finds a direct whole-cell LOS/NLOS switch and a plausible per-UE building-geometry route, which remains unprobed. It also finds that the default 3GPP channel-condition and small-scale channel update periods are zero, and current offered rates are shared across UEs. The researcher selected whole-cell LOS/NLOS comparisons with mobility. An isolated six-UE C++ probe observed all links return the forced whole-cell condition and identical seed/run mobility traces across two invocations. The pinned CPU Torch wheels were downloaded from the Aliyun PyTorch mirror and installed; Python imports and a CPU tensor operation pass. The new Python run for this audit and grant, traffic, and packet-tail evidence remain outstanding. See [RA-ENG-001](docs/missions/RA-ENG-001-feasibility.md) for per-factor verdicts, remaining evidence and limitations.
