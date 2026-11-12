# G1 campaign measurement and statistical method

**Scope:** RA-ENG-007's researcher-approved 160-cell matrix; implementation/reporting method for RA-ENG-008. **Status:** documented measurement rules; results are descriptive simulated evidence.

## Units and estimands

- A cell is one combination of channel (`all-los`, `ue6-nlos`), mobility, offered-load arm, dApp policy, and seed. DL and UL are both measured within each run.
- The independent replicate is the random seed. The five approved seeds are `[11,22,33,44,55]`. Packets, UEs, directions, and time samples are not independent replicates.
- A paired contrast is computed within the same remaining factors, UE, direction, and seed. The factor effect is treated minus reference. For policy-by-channel interaction, first compute `TopKCqi − RoundRobin` within each channel at a matched seed, then subtract the LOS policy effect from the selective-UE6-NLOS policy effect.
- Report run-level mean and sample SD, and a two-sided Student t 95% interval across independent seed values. For five paired seeds this uses df=4 and `t*=2.776`. With one seed no interval is shown. These small-sample intervals are descriptive and rely on independent, comparable seed replicates; they do not establish model validity.

## Packet identity, loss, and censoring

Application packet sequence is keyed by UE and direction. The primary latency distribution uses unique RX packets whose sequence has a recorded TX event in the same run, with one-way delay computed from recorded application event times. The frozen percentile estimator is type 7 (linear interpolation at `(n−1)p`). Report received-latency `n` beside mean, P50, P95, and P99.

`tx_packets` is the number of unique TX sequences; `rx_unique_packets` is the number of unique RX sequences; `matched_rx_packets` counts RX sequences with a corresponding TX; `rx_without_matching_tx` counts RX sequences that cannot be joined; TX/RX duplicate event counts are separate. `lost_or_unreceived_at_stop` is unique TX sequences with no matching RX by the end of collection. It is not labelled network loss: a packet may be dropped, remain in flight, or be censored at stop. No deadline-based loss measure is defined by this campaign.

Application TX rate and RX goodput use unique bytes divided by the configured observation interval after excluding application start-up and receiver drain. Configured offered rate, measured TX rate, and received goodput are distinct quantities. Application one-way delay includes the modeled backhaul and is not pure radio scheduling delay.

## Tail adequacy and missing values

P99 is labelled `at-least-1000-received` only when at least 1,000 matched RX delay samples support the run-level percentile; otherwise it is `exploratory-small-n`. The 1,000-sample threshold is a transparent review flag and does not guarantee tail calibration. If no matched RX samples exist, delay summaries are null and the zero sample count remains visible; rows are not removed.

## Trace validation and exclusions

Before selection, require zero process exit, the serialized application-header schema, exact current campaign source hashes, KPI output, and populated packet-event, MAC-grant, and MAC-demand traces with required headers. Among valid retries, select the highest-numbered complete attempt. Every other attempt remains in the audit with an explicit exclusion reason. Verify all 160 channel/mobility traces: six UEs, at least 120 sampled channel states, expected LOS/NLOS identities, and expected position changes for the mobility arm.

Grant totals are joined to UE identity through observed RNTI-to-UE packet mappings. `prb_symbol_share` divides each UE's applied PRB-symbol grants by the sum observed across UEs in that run and direction. It is a share among observed grants, not cell utilization. Zero-grant UE/direction pairs are retained explicitly.

## Reproduction

From the repository root, with the pinned simulator virtual environment provisioned:

```sh
simulator/ns-3.48/.venv/bin/python -m unittest discover -s campaigns/20261111-g1-integrated-v2/tests -v
env MPLCONFIGDIR=/tmp/mpl-ra-eng-008 simulator/ns-3.48/.venv/bin/python campaigns/20261111-g1-integrated-v2/scripts/analyze_g1_integrated_campaign.py --campaign-root simulator/runs/20261111-g1-integrated-v2 --output-dir results/RA-ENG-008-20261112-audited-v3
```

The analyzer refuses a nonempty output directory. Each attempt has an `artifact-sha256.txt`; curated analysis outputs have `results-sha256.txt`. Do not overwrite either raw run attempts or an existing analysis directory.

## Limitations

The five-seed sample is small. Synthetic selective NLOS and controlled-linear motion are simulator controls; they do not establish propagation or mobility fidelity in a deployed network. Queues, configured rates, app-layer counters, and MAC grants describe different layers. The analysis is descriptive and does not identify a real-world causal mechanism.
