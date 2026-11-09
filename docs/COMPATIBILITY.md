# Version compatibility and environment boundary

**Status:** pinned stack installed, built, and exercised by one upstream NR smoke baseline. Checked 2026-11-09.

## Selected compatible combination

| Component | Pin | Commit | Evidence / role |
|---|---|---|---|
| ns-3 | 3.48 tag | tag object `422ef9dc12d9bcd4ee8f4b1374dffcc029a3675c`; peeled source commit `d2add90b452d600cfb4859baed8e9ea633519447` | ib-ORAN install guide explicitly documents 3.48 |
| 5G-LENA NR | v5.1 tag | tag object `2fab8d9b8b5f823ab8a83495e4239b246182071b`; peeled source commit `cedceadda17392c90587fb9400eb9b1f8c236713` | ib-ORAN guide uses v5.1; CTTC release pairs it with ns-3.48 |
| ns3-ai | `main` | `b8c9858294b1d6a7f122b5154a3ce25057a54740` | ib-ORAN requires newer message interface; upstream says tags 1.0–1.2 predate it |
| Orange ib-ORAN | `main` | `3ea5046389f0eb993cdf01ef6d6d33017e6921bb` | current upstream commit; upstream repository has no release tag in the checked tag list |
| Python | 3.12.3 | host interpreter used in local venv | upstream documented minimum is 3.11+; no Python 3.11 install was needed |

Exact manifest is [here](../manifests/environment.json). The first two identifiers above are annotated tag-object hashes, not commit IDs; the peeled source commit is listed separately. Pin moving branches by commit and tags by both tag object and peeled commit; update only through a documented compatibility review.

## Legacy environment being retired

The historical repository records ns-3.35 (`ac88b75eac1818c673cf2c939a96ac3005b1f051`), 5G-LENA NR v1.2 line (`fe0a1d2a5fb7d1547e46042041288a684893ba9e`), and CTTC NR-U extension (`75a45143b1cd382326876a9597e856338673039a`). They supported the archived coexistence research and are not dependencies of this project. Their local owned checkout is slated for removal only after preservation checks and remote publication.

## Why not select the newest independently

As of the check date, ns-3.49 had been released, but the ib-ORAN tested instructions still specify 3.48 and NR v5.1's official release pairing is ns-3.48. NR v5.2 was listed as under development. No official ib-ORAN-supported 3.49 + NR v5.2 combination was found. Therefore use the documented combination; do not infer compatibility from component recency or undertake an unsupported port.

## Dependencies and host audit

ib-ORAN installation documentation lists Python 3.11+, GCC 11.1+ or Clang 17+, CMake 3.25+, Boost 1.89+, Protobuf 6.33.0+, pybind11 3.0+, and yaml-cpp discoverable by CMake. Host versions were Python 3.12.3, CMake 3.28.3, GCC 13.3.0, Boost 1.83.0, pybind11-dev 2.11.1, yaml-cpp 0.8; protobuf C++ development/compiler were absent. The build used local Boost 1.89.0, Protobuf 6.33.5 (protoc 33.5), pybind11 3.1.0, and yaml-cpp 0.8. Python used project-local CPU Torch 2.9.1+cpu, torchvision 0.24.1+cpu, and Protobuf 6.33.5. No system packages were changed. Full local Python freeze and install logs are under ignored `simulator/logs/`.

## Runtime verification

The NR executable built successfully with the pinned combination; the Python binding imported successfully; one official toy-workload NR run completed with exit status 0. Exact configuration and KPI evidence are in [Mission 1 report](missions/mission-1-installation.md) and the [curated baseline result](../results/mission1-nr-baseline/README.md). This validates this host/build/run combination, not all host configurations or production RIC interoperability.

## Mobility and uncertainties

5G-LENA v5.1 provides ns-3 mobility integration and handover-related capabilities upstream. The pinned ib-ORAN NR scenario calls `SetupFronthaulMobility` and installs `RandomWalk2dMobilityModel` for UEs (0.83 m/s, direction change after 100 m, random initial positions). This is source-confirmed and configured in the baseline; no dedicated mobility validation or controlled fixed-topology comparison was performed. The selected branch snapshots may advance; reproduce using the commits above. Mission 1 verified build/runtime compatibility for this selected snapshot only.

## Environment boundary

The future modern stack belongs under this repository's ignored `simulator/` or an explicitly documented isolated path inside this repo. No symlinks, include paths, libraries, or modules may reference the retired `self-research/source` tree or another project. Legacy patches are historical only and must not be applied to modern sources.

## Official sources

- [ib-ORAN README](https://github.com/Orange-OpenSource/ns3-iboran)
- [ib-ORAN installation guide](https://github.com/Orange-OpenSource/ns3-iboran/blob/main/doc/installation.md)
- [ib-ORAN KPI definitions](https://github.com/Orange-OpenSource/ns3-iboran/blob/main/doc/kpis.md)
- [ns-3 release tags](https://gitlab.com/nsnam/ns-3-dev/-/tags)
- [CTTC NR v5.1 release announcement](https://cttc-lena.gitlab.io/5g-lena-website/blog/36/)
- [5G-LENA feature roadmap](https://5g-lena.cttc.es/features/roadmap/)
- [ns3-ai repository](https://github.com/hust-diangroup/ns3-ai)
