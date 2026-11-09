# M1-DR-02 — Use CPU-only Torch for the baseline environment

- **Date:** 2026-11-09
- **Status:** accepted for this environment
- **Context:** ib-ORAN requirements did not pin Torch. Initial pip resolution selected a CUDA-enabled Torch build and large NVIDIA dependencies.
- **Alternatives:** continue unconstrained CUDA package resolution; pin CPU-only Torch/torchvision; omit Torch and test whether the runner imports without it.
- **Decision:** install Torch 2.9.1+cpu and torchvision 0.24.1+cpu in the project venv.
- **Reason:** the toy baseline requires model/runtime Python dependencies but does not need GPU acceleration. The initial resolution was stopped before Torch/CUDA packages were installed. Rationale is retrospective from observed pip resolution and CPU-only use.
- **Consequences:** CPU execution is reproducible for this smoke baseline; performance is not representative of a GPU deployment.
- **Disadvantages:** a future training workload may require separately validated accelerator libraries.
- **Evidence:** local pip attempt note, CPU install log, Python freeze, [Mission 1 report](../missions/mission-1-installation.md).
