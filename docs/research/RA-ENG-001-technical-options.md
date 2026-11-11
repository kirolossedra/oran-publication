# RA-ENG-001 technical options and researcher gates

**Date:** 2026-11-11. These are engineering options derived from pinned source, not scientific decisions. See the [capability matrix](RA-ENG-001-capability-matrix.md) and [feasibility report](../missions/RA-ENG-001-feasibility.md).

## Channel intervention options

| Option | Technical basis | Fidelity and risks | Status |
|---|---|---|---|
| **A. Selective obstruction using Buildings condition model** | The pinned NR helper accepts `Buildings`; ns-3's `BuildingsChannelConditionModel` evaluates each gNB/UE position pair and determines LOS/NLOS from whether a building blocks the line. A carefully placed, static obstacle could leave five links LOS and block the target link while holding UE coordinates constant. | Closest source-supported route to a selective link perturbation. Requires adding a building and building mobility metadata, using the Buildings condition factory, and checking all six link states with a probe. This combines UMi path-loss equations with geometric obstruction state; the researcher must review whether that model is appropriate for the proposed question. It is not evidence of a real factory channel. | **Preferred engineering probe if researcher retains a single-UE intervention. Not implemented.** |
| **B. Custom per-link condition model** | The `ChannelConditionModel` API receives both endpoint mobility models; node IDs can distinguish a selected gNB/UE pair. | Precise control, but requires a new model/factory integration and explicit trace validation. Larger maintenance surface than geometry. | **Fallback for researcher review if option A cannot realize the intended comparison. Not implemented.** |
| **C. Whole-cell forced LOS versus NLOS** | Pinned `NrChannelHelper` maps its helper `LOS`/`NLOS` options to `AlwaysLos`/`NeverLos`, which return one class for every endpoint pair. The existing `nr-channel-setup-test` passes. The local isolated six-UE probe observed all six link conditions for each setting. | Easy paired switch, with every UE link receiving the same condition class. Probe checks condition values, not propagation metrics or the full ib-ORAN scenario. | **Selected by the researcher on 2026-11-11 and observed in the isolated helper probe.** |

## Mobility choices

| Option | What it answers | Evidence needed before use |
|---|---|---|
| Keep upstream `RandomWalk2d` | Adds mobility while retaining the existing movement model. It does not imply obstacle crossings or LOS/NLOS transitions with the default condition period. | **Selected by the researcher as the primary position setup on 2026-11-11.** An isolated six-UE recreation produced byte-identical position samples at 0, 60 and 130 s across two processes with seed 1/run 1. This does not establish repeatability after the full scenario's other RNG consumers are created. Whole-cell forced LOS/NLOS is the condition intervention, so mobility need not create blockage transitions. |
| Fixed positions for a separately approved comparison | Pinned ns-3 provides `ConstantPositionMobilityModel`, also used for the gNB in the current scenario. Make UE model selection configurable and set explicit initial positions. | Verify positions remain constant and record them. This changes the selected mobile-primary setup and requires researcher approval before use. |
| Waypoint or constant-velocity trajectory | Pinned ns-3 provides `WaypointMobilityModel::AddWaypoint` and `ConstantVelocityMobilityModel::SetVelocity`; waypoint motion interpolates linearly and can hold at a point by repeating positions at distinct times. | Make model selection configurable, set explicit starts/path and record course changes. Match target/control UE paths. This is a controlled alternative, not selected for the current primary setup. |

## Control and measurement options

- Keep an xApp behavior fixed while comparing two stock dApp selection algorithms only after a small saturated pilot proves that the emitted controls produce distinct **applied** grants. Candidate source options include `RoundRobin` and `TopKCqi`; this audit does not select the pair.
- Preserve RNTI, direction, decision ID, requested RBGs, max-bound values, applied RBG ranges, MCS/TBS, and packet outcomes in synchronized records. A nonbinding xApp maximum is not a resource allocation guarantee.
- Add six independently configured UE traffic roles with separate UL/DL rate, packet size, source mode, and start/stop values. The current `dlBitRate`/`ulBitRate` values are shared across all UEs and the current app sends finite dataset payloads.
- Add per-packet TX simulation time and sequence identity at the application layer; match RX by run, flow and sequence. Report loss/censoring alongside received-packet latency distributions. Do not infer P95/P99 from current aggregate `delaySum`.
- For later packet-tail reporting, state the estimator (a transparent option is nearest-rank empirical quantiles, rank `ceil(p*n)`), report received/matched sample counts for every UE, flow, direction and run, and aggregate uncertainty across independent runs. At P99, the expected upper-tail count is `0.01*n`; small packet counts therefore yield coarse and unstable tail estimates. The researcher must approve any minimum sample size and stopping rule with the protocol.

## Required, optional, and scope-changing work

| Class | Items | Implementation risk and dependencies |
|---|---|---|
| Required for the selected whole-cell/mobile direction | Expose the LOS/NLOS factory as a config choice; retain matched per-UE position and condition/channel-state records; establish the full scenario's repeatable positions; independently configure offered load before a loaded comparison; add per-packet identity/timestamps and preserve loss/censoring; record applied grants before interpreting policy effects. | Config and trace hooks are **small**; per-UE traffic/source changes and packet instrumentation are **medium**, touching C++, Python, YAML and output retention. Full Python scenario requires the exact pinned CPU Torch dependencies. |
| Optional engineering diagnostics | Extra static/control position arm, additional mobility samples, fairness calculation from consistent per-UE delivered goodput, or channel metric traces beyond those required for the chosen endpoint. | **Small to medium**, depending on whether current trace sources expose the required fields; not prerequisites for claiming that the installed code offers these interfaces. |
| Scientifically different; researcher approval required | Selective one-UE NLOS instead of whole-cell LOS/NLOS; calibrated indoor/factory model instead of UMi; stationary primary study instead of the selected mobile setup; new scheduler/policy comparison. | Selective Buildings geometry is **small/medium** and unprobed. A custom per-link model is **major**. Channel-scope and mobility changes alter the scientific comparison and cannot be selected as implementation defaults. |

The risk labels describe integration surface and dependencies, not delivery-time estimates.

## Recorded researcher decisions

1. Use a **whole-cell LOS/NLOS** comparison.
2. Use **mobility** in the primary setup, retaining the upstream `RandomWalk2d`; an isolated same-seed probe passed, while scenario-level stream repeatability remains unverified.
3. Restore the exact pinned simulator under ignored `simulator/`. The four source commits match `manifests/environment.json`; the C++ target and bridge binding build succeeded. The locked CPU Torch wheels remain unavailable: temporary DNS-over-TLS resolves the hosts, but the official index and alternate CDN time out over HTTPS.

The primary-literature novelty decision and full experimental protocol remain separate human-owned gates. The source feasibility verdict authorizes only bounded probes; it does not establish the final campaign protocol.
