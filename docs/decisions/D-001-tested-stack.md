# D-001 — Use the documented ib-ORAN stack

- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** ib-ORAN is coupled to simulator and Python bridge interfaces; independently choosing newest releases risks incompatibility.
- **Alternatives:** combine latest standalone releases; use upstream ib-ORAN documented versions; port unsupported versions.
- **Decision:** select ns-3.48, NR v5.1, ns3-ai pinned `main`, ib-ORAN pinned `main`, Python 3.11+.
- **Reason:** ib-ORAN's current installation guide explicitly documents this combination, and CTTC pairs NR v5.1 with ns-3.48. The stated reason is a retrospective decision from current upstream evidence, not a claim of historical deliberation.
- **Consequences:** reproducible known-supported target; a newer ns-3 release remains unused until upstream compatibility is established.
- **Disadvantages:** branch components require commit pinning; some host dependencies are older/missing.
- **Evidence:** [compatibility record](../COMPATIBILITY.md), [official install guide](https://github.com/Orange-OpenSource/ns3-iboran/blob/main/doc/installation.md).
