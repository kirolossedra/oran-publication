# Validation index

- [test_scheduler.py](test_scheduler.py): RoundRobin wrap regression,
  TopKCqi ranking/ties, run-provenance and 160-cell bookkeeping
- [test_sanity.py](test_sanity.py): throughput fairness and
  continuously backlogged grant-gap diagnostics
- [test_packet_analysis.py](test_packet_analysis.py): packet
  matching, duplicate/reorder/loss and percentile edge cases

Run `python3 -m unittest discover -s tests -v` in the provisioned
environment, or use [sanity.sh](../experiment-scripts/sanity.sh),
which runs regressions before compilation.
