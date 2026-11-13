#!/usr/bin/env python3
"""Build an explicit one-seed rate/reliability calibration report from campaign analysis CSVs."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"required analyzer output missing: {path}")
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))

def number(row: dict, key: str, default: float = 0.0) -> float:
    value = row.get(key)
    return default if value in ("", None, "None") else float(value)

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise SystemExit(f"refusing to write empty calibration table: {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, required=True,
                        help="output directory already populated by analyze_campaign.py")
    args = parser.parse_args()
    out = args.analysis_dir.resolve()
    metrics = read_csv(out / "per-run-ue-metrics.csv")
    grants = read_csv(out / "per-run-ue-grants.csv")
    demand = read_csv(out / "per-run-ue-demand.csv")
    audit = read_csv(out / "run-audit.csv")
    selected = [r for r in audit if r.get("selected_for_analysis", "").lower() == "true"]
    valid = [r for r in selected if r.get("measurement_complete", "").lower() == "true"]
    if len(selected) != 8 or len(valid) != 8 or len(metrics) != 96:
        raise SystemExit(f"calibration incomplete: selected={len(selected)}/8 valid={len(valid)}/8 UE-directions={len(metrics)}/96")
    grant_map = {(r["cell_id"], r["direction"], r["ue_index"]): r for r in grants}
    demand_map = {(r["cell_id"], r["direction"], r["ue_index"]): r for r in demand}
    enriched = []
    summaries = {}
    for r in metrics:
        match = re.search(r"cal-(10|25|50|100)mbps", r["cell_id"])
        if not match:
            raise SystemExit(f"unexpected calibration cell id: {r['cell_id']}")
        rate = int(match.group(1))
        g = grant_map.get((r["cell_id"], r["direction"], r["ue_index"]), {})
        d = demand_map.get((r["cell_id"], r["direction"], r["ue_index"]), {})
        row = {
            "cell_id": r["cell_id"], "offered_mbps_per_ue_per_direction": rate,
            "policy": r["policy"], "seed": r["seed"], "channel": r["channel"],
            "mobility": r["mobility"], "direction": r["direction"], "ue_index": r["ue_index"],
            "configured_offered_mbps": number(r, "offered_bps_configured") / 1e6,
            "application_tx_mbps": number(r, "application_tx_rate_bps") / 1e6,
            "received_goodput_mbps": number(r, "rx_goodput_bps") / 1e6,
            "tx_packets": int(number(r, "tx_packets")), "rx_packets": int(number(r, "rx_unique_packets")),
            "pdr": number(r, "pdr", float("nan")),
            "lost_or_unreceived_at_stop": int(number(r, "lost_or_unreceived_at_stop")),
            "received_latency_n": int(number(r, "received_latency_n")),
            "p50_latency_ms": r.get("p50_latency_ms"), "p95_latency_ms": r.get("p95_latency_ms"),
            "p99_latency_ms": r.get("p99_latency_ms"), "p99_sample_adequacy": r.get("p99_sample_adequacy"),
            "mac_actual_throughput_mbps": d.get("mean_actual_throughput_mbps"),
            "mac_achievable_rate_mbps": d.get("mean_achievable_rate_mbps"),
            "grant_count": int(number(g, "grant_count")), "prb_symbols": int(number(g, "prb_symbols")),
            "prb_symbol_share": g.get("prb_symbol_share"), "mean_mcs": g.get("mean_mcs"),
            "mean_reported_cqi": d.get("mean_reported_cqi"),
            "queue_nonempty_fraction": d.get("fraction_nonempty_queue"),
            "mean_queue_bytes": d.get("mean_queue_bytes"), "max_queue_bytes": d.get("max_queue_bytes"),
        }
        enriched.append(row)
        key = (rate, r["policy"], r["direction"])
        summaries.setdefault(key, []).append(row)
    if len({(r["cell_id"], r["direction"], r["ue_index"]) for r in enriched}) != 96:
        raise SystemExit("duplicate calibration UE/direction rows detected")
    aggregate = []
    for (rate, policy, direction), rows in sorted(summaries.items()):
        tx = sum(r["tx_packets"] for r in rows)
        rx = sum(r["rx_packets"] for r in rows)
        received_n = sum(r["received_latency_n"] for r in rows)
        aggregate.append({
            "offered_mbps_per_ue_per_direction": rate, "six_ue_configured_offered_mbps": sum(r["configured_offered_mbps"] for r in rows),
            "policy": policy, "seed": rows[0]["seed"], "direction": direction, "ue_count": len(rows),
            "six_ue_application_tx_mbps": sum(r["application_tx_mbps"] for r in rows),
            "six_ue_received_goodput_mbps": sum(r["received_goodput_mbps"] for r in rows),
            "six_ue_mac_actual_throughput_mbps": sum(number(r, "mac_actual_throughput_mbps") for r in rows),
            "tx_packets": tx, "rx_packets": rx, "pdr": rx / tx if tx else None,
            "lost_or_unreceived_at_stop": sum(r["lost_or_unreceived_at_stop"] for r in rows),
            "received_latency_n": received_n,
            "p95_latency_ms_max_ue": max((number(r, "p95_latency_ms", float("-inf")) for r in rows), default=None),
            "p99_latency_ms_max_ue": max((number(r, "p99_latency_ms", float("-inf")) for r in rows), default=None),
            "ue_with_under_1000_latency_samples": sum(r["received_latency_n"] < 1000 for r in rows),
            "actual_grants_total": sum(r["grant_count"] for r in rows),
            "prb_symbols_total": sum(r["prb_symbols"] for r in rows),
            "mean_queue_bytes_across_ues": sum(number(r, "mean_queue_bytes") for r in rows) / len(rows),
            "max_queue_bytes": max(number(r, "max_queue_bytes") for r in rows),
        })
    if len(aggregate) != 16:
        raise SystemExit(f"expected 16 rate/policy/direction summaries, got {len(aggregate)}")
    for name in ("reliability-calibration-per-ue.csv", "reliability-calibration-summary.csv"):
        if (out / name).exists():
            raise SystemExit(f"refusing to overwrite existing analysis file: {out/name}")
    write_csv(out / "reliability-calibration-per-ue.csv", enriched)
    write_csv(out / "reliability-calibration-summary.csv", aggregate)
    lines = [
        "# G1 high-throughput rate/reliability calibration", "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "**Status:** one-seed engineering calibration only. Rates are not PI-selected scientific operating points. The exploratory PDR target of 99.999% is not established here and this is not a URLLC claim.",
        "",
        "The four offered rates (10/25/50/100 Mbps per UE in both directions) were run at seed 11, all-LOS, stationary, with RoundRobin and TopKCqi. Each summary row aggregates six UEs in one direction. Latency maxima below are the maximum of six per-UE percentiles, not a pooled six-UE percentile; use the per-UE CSV for samples, PDR/loss, queue, CQI/MCS, grant, and PRB details.",
        "",
        "| Rate Mbps/UE | Policy | Dir | Offered Mbps | TX Mbps | Goodput Mbps | MAC actual Mbps | PDR | Lost/unreceived | RX latency n | max UE P95 ms | max UE P99 ms | Grants | Mean queue B | Max queue B |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in aggregate:
        def fmt(value, digits=3):
            return "N/A" if value is None else f"{value:.{digits}f}"
        lines.append("| {rate} | {policy} | {direction} | {offered:.2f} | {tx:.2f} | {goodput:.2f} | {mac:.2f} | {pdr} | {loss} | {n} | {p95} | {p99} | {grants} | {meanq:.1f} | {maxq:.0f} |".format(
            rate=r["offered_mbps_per_ue_per_direction"], policy=r["policy"], direction=r["direction"],
            offered=r["six_ue_configured_offered_mbps"], tx=r["six_ue_application_tx_mbps"],
            goodput=r["six_ue_received_goodput_mbps"], mac=r["six_ue_mac_actual_throughput_mbps"],
            pdr=fmt(r["pdr"], 6), loss=r["lost_or_unreceived_at_stop"], n=r["received_latency_n"],
            p95=fmt(r["p95_latency_ms_max_ue"]), p99=fmt(r["p99_latency_ms_max_ue"]),
            grants=r["actual_grants_total"], meanq=r["mean_queue_bytes_across_ues"], maxq=r["max_queue_bytes"]))
    lines += ["", "## Interpretation boundary", "",
        "Use measured delivered goodput and loss to identify the observed load region. One seed does not estimate run-to-run uncertainty; packets are measurements, not independent simulation replicates. The PI selects final operating rates after review. Application delay includes modeled backhaul; no application deadline was specified.",
        "", "## Files", "",
        "- reliability-calibration-summary.csv: six-UE direction totals and worst-UE latency tails",
        "- reliability-calibration-per-ue.csv: each UE and direction, including loss, samples, MAC grants, queues, CQI and MCS",
        "- per-run-ue-metrics.csv, per-run-ue-grants.csv, per-run-ue-demand.csv: generic analyzer evidence",
        "- run-audit.csv, channel-mobility-audit.csv: run validity evidence",
        ""]
    report = out / "reliability-calibration-report.md"
    report.write_text("\n".join(lines) + "\n")
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != "reliability-calibration-sha256.txt")
    (out / "reliability-calibration-sha256.txt").write_text("".join(
        f"{digest(p)}  {p.name}\n" for p in files))
    print(f"Calibration complete: 8/8 runs, 16 aggregate directions, report={report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
