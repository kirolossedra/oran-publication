# Version compatibility and environment boundary

**Status:** source-verified upstream pins, selected but not installed. Checked 2026-11-09.

## Selected compatible combination

| Component | Pin | Commit | Evidence / role |
|---|---|---|---|
| ns-3 | 3.48 tag | `422ef9dc12d9bcd4ee8f4b1374dffcc029a3675c` | ib-ORAN install guide explicitly documents 3.48 |
| 5G-LENA NR | v5.1 tag | `2fab8d9b8b5f823ab8a83495e4239b246182071b` | ib-ORAN guide uses v5.1; CTTC release pairs it with ns-3.48 |
| ns3-ai | `main` | `b8c9858294b1d6a7f122b5154a3ce25057a54740` | ib-ORAN requires newer message interface; upstream says tags 1.0–1.2 predate it |
| Orange ib-ORAN | `main` | `3ea5046389f0eb993cdf01ef6d6d33017e6921bb` | current upstream commit; upstream repository has no release tag in the checked tag list |
| Python | 3.11+ | runtime pin to record at install | upstream documented minimum |

Exact manifest is [here](../manifests/environment.json). Pinning a moving branch by commit makes the chosen snapshot reproducible; update only through a documented compatibility review.

## Legacy environment being retired

The historical repository records ns-3.35 (`ac88b75eac1818c673cf2c939a96ac3005b1f051`), 5G-LENA NR v1.2 line (`fe0a1d2a5fb7d1547e46042041288a684893ba9e`), and CTTC NR-U extension (`75a45143b1cd382326876a9597e856338673039a`). They supported the archived coexistence research and are not dependencies of this project. Their local owned checkout is slated for removal only after preservation checks and remote publication.

## Why not select the newest independently

As of the check date, ns-3.49 had been released, but the ib-ORAN tested instructions still specify 3.48 and NR v5.1's official release pairing is ns-3.48. NR v5.2 was listed as under development. No official ib-ORAN-supported 3.49 + NR v5.2 combination was found. Therefore use the documented combination; do not infer compatibility from component recency or undertake an unsupported port.

## Dependencies and host audit

ib-ORAN installation documentation lists Python 3.11+, GCC 11.1+ or Clang 17+, CMake 3.25+, Boost 1.89+, Protobuf 6.33.0+, pybind11 3.0+, and yaml-cpp discoverable by CMake. Host audit found Python 3.12.3, CMake 3.28.3, GCC 13.3.0, Boost 1.83.0, pybind11-dev 2.11.1, yaml-cpp 0.8; Python 3.11, protobuf development/compiler packages were not found. Thus Boost, pybind11, Python interpreter selection, and protobuf need resolution before installation. No packages were removed or installed in this migration.

## Mobility and uncertainties

5G-LENA v5.1 provides ns-3 mobility integration and handover-related capabilities upstream. That does not establish mobility was exercised by ib-ORAN's specific agents or scenario. Verify by source inspection and a focused test before using UE motion. The selected branch snapshots may advance; reproduce using the commits above. Upstream-supported status is not equivalent to independent build verification.

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
