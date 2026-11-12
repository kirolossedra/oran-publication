# LOS→NLOS→LOS O-RAN research implementation

**Authority:** PI-directed scenario change. Source implementation is opt-in. Numerical research choices remain unset and no full simulation has been executed by the assistant.

## Exact simulation behavior

One gNB, six UEs, UE6 the moving target at 1 m/s, five other UEs stationary. Compare (a) all-LOS and (b) UE6 LOS→NLOS→LOS during the same 20-second run. In both arms the same traffic, seed, dApp, and xApp selection are used. The new C++ condition wrapper returns NLOS only for the UE6 link between explicitly configured start and end seconds, and LOS otherwise; pathloss and 3GPP fading share that condition model. Exact boundary events are logged as CHANNEL_TRANSITION alongside periodic CHANNEL_STATE records.

## What O-RAN actually contributes

The stock Orange ib-ORAN xApp is switched between **Bypass** (unconstrained upper grants) and **Clamp** (feedback-derived per-UE RBG maximums). Stock dApp controls are **RoundRobin** and **GreedyPropFairness** (PF-like research selector, not commercially verified PF scheduling). A matched comparison isolates the effect of the xApp bound under the same dApp. This is a real xApp→shared-memory→MAC actuator, not just a scheduler name change. **RBG maxima do not guarantee UE6 a minimum allocation, reliability, or latency.**

**QoS-aware scheduling is NOT implemented or claimed:** the current basic UDP experiment has not established per-flow 5QI, delay-budget, and criticality information suitable for enforcing latency-sensitive traffic. A new algorithm must not be labeled QoS-aware merely because the name includes Criticality.

## Changed source paths

- simulator/overrides/iboran/model/iboran_ran_environment/iboran-nr-environment.cc — in-run condition and boundary trace
- simulator/overrides/iboran/model/iboran_ran_environment/iboran-ran-common.cc — target-only 1 m/s mode
- simulator/overrides/iboran/model/iboran_ran_environment/iboran-ran-params.h and .cc — config fields
- simulator/overrides/iboran/model/utils/config_store.py — Python config schema
- simulator/overrides/iboran/SHA256SUMS — source override manifest
- configs/los-nlos-transition.json — separate, researcher-gated run specification
- experiment-scripts/run_los_nlos_transition.py — matched trials and log gate
- experiment-scripts/analyze_los_nlos_transition.py — phase/UE/direction packet/CQI analysis
- tests/test_los_nlos_transition.py — schema and transition diagnostics

## How to run after PI supplies the missing numeric fields

The JSON intentionally has null values for transition start/end, bandwidth, four per-UE offered bitrates, and dApp k. The system **cannot truthfully call the proposed experiment fully approved numerically** until those values are chosen. The runner fails before touching simulation if they remain null.

```bash
python experiment-scripts/run_los_nlos_transition.py --plan-only
# After filling PI-approved values in configs/los-nlos-transition.json, and provisioning pinned ns-3, ib-ORAN, venv, and sources:
python -m unittest discover -s tests -v
bash experiment-scripts/sanity.sh --apply-overrides
# CAUTION: sanity.sh itself still runs the OLD 20-case G1 experiment. Do not confuse its results with transition validation.
cd simulator/ns-3.48 && ./ns3 build ns3iboran_nr -j 2 && cd ../..
python experiment-scripts/run_los_nlos_transition.py --limit 2
python experiment-scripts/run_los_nlos_transition.py
python experiment-scripts/analyze_los_nlos_transition.py --campaign-root simulator/runs/los-nlos-transition-engineering-v1 --output results/los-nlos-transition-engineering-v1/phase-metrics.csv
```

## Scientific and reproducibility cautions

- The all-LOS arm and transition arm must have matched seed, offered rates, controller, geometry, and window boundaries. Per-phase results are cohort-labeled by packet **TX** time, so late RX remains attributed to the original TX phase.
- Packet not received by sink stop is not necessarily physical-layer loss. Received-only P99 must always be reported with PDR and received sample counts. The analyzer does not currently calculate grants per phase; legacy grant traces are still available for extended validation.
- A change in wrapper CHANNEL_STATE labels alone **does not verify the underlying PHY response**. Verify measured per-UE CQI, MCS, delivered goodput, applied grants and per-phase delays before scientific claims. Verify 3GPP condition-cache handling and control-loop timescale in the pinned model.
- The 500 Mbps ambition is not assumed feasible or imposed on all UEs. Real capacity depends on bandwidth, antennas, TDD, channel, MCS and control overhead. Existing 6 Mbps G1 configuration is left untouched as historical evidence.
- Only one seed is provided as an **engineering diagnostic**; this is not a formal published protocol. The PI must authorize sample count, thresholds, final scheduling policy and research hypothesis separately.
- Current Orange Clamp acts via maximum resource bounds; it is not a guaranteed-QoS controller. A genuinely QoS-directed xApp and any intra-UE UL/DL priority handling require additional design and validation.
- There is no current WSL simulator available in this assistant runtime to compile and execute the changes; any claimed successful simulation would be false.

See [issue #26](https://github.com/kirolossedra/oran-publication/issues/26) for governance and source limitations.
