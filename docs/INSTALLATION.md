# Installation and reproducibility plan

No simulator installation or lengthy build is part of the migration mission. This page records the upstream-supported procedure to use in a separately authorized installation mission; it is not evidence of a local installation.

## Selected layout

```text
self-research/
├── source/                 # historical NR-U archive only; not reused
└── oran-publication/
    ├── simulator/          # future ignored checkout/build root
    │   ├── ns-3.48/
    │   ├── ns-3.48/contrib/nr/       # 5G-LENA v5.1
    │   ├── ns-3.48/contrib/ai/       # ns3-ai pinned commit
    │   └── ns-3.48/contrib/iboran/   # ib-ORAN pinned commit
    └── ... research docs/config/results
```

Layout is proposed; upstream clone instructions place modules in the ns-3 tree. Confirm exact directory conventions with pinned installation docs before execution. Keep source/build outputs ignored and do not link to legacy headers or libraries.

## Reproduction outline

1. Record OS, disk free space, compiler, Python interpreter, and dependency versions.
2. Provision Python 3.11 and library versions meeting [the compatibility manifest](../manifests/environment.json), preferably in an isolated environment where feasible; avoid removing shared host packages.
3. Clone exact commits/tags independently into the dedicated simulator directory. The official guide specifies ns-3.48, NR v5.1, ns3-ai `main`, and ib-ORAN; it also notes its ns3-ai example directory may need exclusion for build compatibility. Do not execute that cleanup without verifying the pinned tree and documenting effects.
4. Configure and build with the exact upstream commands, preserving full logs and configuration output.
5. Run upstream smoke examples, then one documented ib-ORAN scenario; save configuration, seeds, logs, and raw outputs under a unique run ID.
6. Record source `git rev-parse HEAD`, dirty status/patches, dependency lock/version output, command lines, and SHA256 hashes.

Exact commands will be transcribed from the pinned upstream guide during the installation mission, not guessed here. A complete run record is required before reporting any result.
