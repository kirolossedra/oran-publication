# Measurement index

- [Packet and MAC grant metrics](packet-grant-metrics.md):
  offered rate vs application TX Mbps vs received goodput Mbps, loss/PDR,
  P50/P95/P99, real DCI grants/PRB allocation and queue demand
- [Packet identity limitation](packet-identity-limitation.md):
  original PacketTag identities were invalid; serialized headers are required
- [Load calibration](load-calibration.md):
  seed-11 low and contending traffic calibration and associated limitations

P99 computed only from received packets is conditional on delivery:
for a UE with no receptions, percentile latency is undefined, not zero.
Always show packet counts and throughput beside latency.
