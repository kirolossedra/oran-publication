# RA-ENG-001 technical options and researcher gates

**Date:** 2026-11-11. These are engineering options derived from pinned source, not scientific decisions. See the [capability matrix](RA-ENG-001-capability-matrix.md) and [feasibility report](../missions/RA-ENG-001-feasibility.md).

## Channel intervention options

| Option | Technical basis | Fidelity and risks | Status |
|---|---|---|---|
| **A. Selective obstruction using Buildings condition model** | The pinned NR helper accepts `Buildings`; ns-3's `BuildingsChannelConditionModel` evaluates each gNB/UE position pair and determines LOS/NLOS from whether a building blocks the line. A carefully placed, static obstacle could leave five links LOS and block the target link while holding UE coordinates constant. | Closest source-supported route to a selective link perturbation. Requires adding a building and building mobility metadata, using the Buildings condition factory, and checking all six link states with a probe. This combines UMi path-loss equations with geometric obstruction state; the researcher must review whether that model is appropriate for the proposed question. It is not evidence of a real factory channel. | **Preferred engineering probe if researcher retains a single-UE intervention. Not implemented.** |
| **B. Custom per-link condition model** | The `ChannelConditionModel` API receives both endpoint mobility models; node IDs can distinguish a selected gNB/UE pair. | Precise control, but requires a new model/factory integration and explicit trace validation. Larger maintenance surface than geometry. | **Fallback for researcher review if option A cannot realize the intended comparison. Not implemented.** |
| **C. Whole-cell forced LOS versus NLOS** | Pinned `NrChannelHelper` maps its helper `LOS`/`NLOS` options to `AlwaysLos`/`NeverLos`, which return one class for every endpoint pair. | Easy paired switch, but changes the intervention from one challenged UE to all cell links. Changes scientific meaning and may change every UE's propagation regime. | **Do not proceed without explicit researcher approval of revised scope.** |

## Mobility choices

| Option | What it answers | Evidence needed before use |
|---|---|---|
| Keep upstream `RandomWalk2d` | Adds mobility while retaining the existing movement model. It does not imply obstacle crossings or LOS/NLOS transitions with the default condition period. | Same-seed position trace comparison across policy/load arms; per-UE position and condition telemetry; document random-stream sensitivity. |
| Fixed positions for the first controlled comparison | Makes geometry constant while isolating channel state/load/policy effects. The current function must be given a fixed-position mode. | Verify positions are constant; verify LOS/NLOS state and radio metric differ only as intended. This changes a mobile-primary framing and needs researcher approval. |
| Waypoint or constant-velocity target trajectory | Can produce an interpretable, repeatable path if the chosen model exists in the pinned ns-3 and uses explicit waypoints/speeds. | Verify exact available model API in the local pin; store trajectory points and seed; hold target/control UE paths matched. No robot planner is needed. |

## Control and measurement options

- Keep an xApp behavior fixed while comparing two stock dApp selection algorithms only after a small saturated pilot proves that the emitted controls produce distinct **applied** grants. Candidate source options include `RoundRobin` and `TopKCqi`; this audit does not select the pair.
- Preserve RNTI, direction, decision ID, requested RBGs, max-bound values, applied RBG ranges, MCS/TBS, and packet outcomes in synchronized records. A nonbinding xApp maximum is not a resource allocation guarantee.
- Add six independently configured UE traffic roles with separate UL/DL rate, packet size, source mode, and start/stop values. The current `dlBitRate`/`ulBitRate` values are shared across all UEs and the current app sends finite dataset payloads.
- Add per-packet TX simulation time and sequence identity at the application layer; match RX by run, flow and sequence. Report loss/censoring alongside received-packet latency distributions. Do not infer P95/P99 from current aggregate `delaySum`.

## Researcher decisions required before RA-ENG-002

1. Retain a **single-UE LOS/NLOS perturbation** using explicit obstacle geometry, or approve a **whole-cell LOS/NLOS** comparison as a revised intervention. These are not equivalent.
2. Keep controlled UE mobility in the primary setup, or approve a **fixed-position** primary comparison with mobility deferred.
3. Confirm the working location of the already-pinned ignored simulator environment (the expected `simulator/` directory is absent here), or authorize a separately documented restoration if it is genuinely unavailable.

The primary-literature novelty decision and full experimental protocol remain separate human-owned gates. No experiment campaign is authorized by the feasibility verdict.
