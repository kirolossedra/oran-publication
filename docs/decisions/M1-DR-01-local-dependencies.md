# M1-DR-01 — Provision build dependencies locally

- **Date:** 2026-11-09
- **Status:** accepted for this environment
- **Context:** host Boost 1.83 and pybind11 2.11.1 were below upstream requirements; Protobuf compiler/development packages were missing.
- **Alternatives:** upgrade system packages; install into the project-local prefix/venv; defer the baseline.
- **Decision:** use a micromamba prefix under simulator/envs/cpp and a Python venv under simulator/ns-3.48/.venv. Required C++ package specs were libboost-devel=1.89.0, libprotobuf=6.33.5, yaml-cpp=0.8.
- **Reason:** meets the pinned stack requirements without changing host packages or other projects. This rationale is retrospective, reconstructed from host audit and install logs.
- **Consequences:** configure/run need local CMAKE_PREFIX_PATH and LD_LIBRARY_PATH; environment consumes project disk.
- **Disadvantages:** current local prefixes are host-specific and not committed; clean-host provisioning needs repeatable package resolution.
- **Evidence:** [Mission 1 report](../missions/mission-1-installation.md), environment manifest, local dependency transaction log.
