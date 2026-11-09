# M1-DR-03 — Use the upstream toy NR scenario for installation validation

- **Date:** 2026-11-09
- **Status:** completed
- **Context:** acceptance required a real NR run and verification of simulator/Python control integration, without beginning custom load or policy research.
- **Alternatives:** implement the proposed latency-sensitive traffic immediately; run upstream toy configuration; validate build only.
- **Decision:** run the documented NR runner with dataset toy, dApp ibTopKCqi, k=3, RNG run 5, and xApp Bypass; save dApp scheduler log.
- **Reason:** exercises the upstream NR path, Python bridge, dApp and xApp initialization while keeping research changes out of the installation mission. Bypass was the configured upstream default, so it validates invocation but is not evidence of restrictive resource bounding. This rationale is retrospective from acceptance scope and effective config.
- **Consequences:** successful NR/control smoke test and inspectable outputs; results are not from the proposed workload.
- **Disadvantages:** toy image/embedding traffic and random-walk UEs do not isolate the planned policy/load variables; Bypass does not establish constrained xApp behavior.
- **Evidence:** full local run log/trace and effective config; curated [baseline evidence](../../results/mission1-nr-baseline/README.md); [Mission 1 report](../missions/mission-1-installation.md).
