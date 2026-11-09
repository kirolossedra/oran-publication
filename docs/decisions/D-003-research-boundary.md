# D-003 — Study radio-system behavior through available control hooks

- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** research compares RAN allocation policies and user-plane outcomes in a modeled NR cell.
- **Alternatives:** build an elaborate external RIC stack; use ib-ORAN's simulator-integrated control abstractions; study legacy unlicensed coexistence.
- **Decision:** focus on 5G RAN wireless-system behavior using ib-ORAN control capabilities; leave production external RIC infrastructure out of scope.
- **Reason:** directly matches the human-defined scenario and emphasis. Not a claim that simulator control interfaces are standardized or production-ready.
- **Consequences:** measure radio and per-UE performance while documenting abstraction boundaries.
- **Disadvantages:** results are simulator-specific; interface timing/semantics require validation.
- **Evidence:** migration mission requirements and upstream ib-ORAN [architecture](https://github.com/Orange-OpenSource/ns3-iboran).
