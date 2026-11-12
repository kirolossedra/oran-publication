# Analysis scripts

Analysis code will define units, input schema, missing-data handling, percentile estimator, and sample-count gates. Preserve raw inputs independently and make figures reproducible from committed code and documented inputs.

`prepare_g1_radio_mobility_run.py` validates and writes one complete run config from the pinned ib-ORAN defaults plus a scenario override. `validate_g1_radio_mobility_pair.py` checks paired radio/mobility traces, conditions, positions, node identities and RNTI mappings. These are engineering checks only; they do not estimate treatment effects.
