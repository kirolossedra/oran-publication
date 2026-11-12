#!/usr/bin/env python3
"""Join packet, MAC-demand and applied-grant evidence for load-calibration cases."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", required=True,
                        help="CASE_NAME=directory with logs/ and analysis/ outputs; repeatable")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    summaries: list[dict] = []
    unmatched_grants: list[dict] = []
    demand_codes: dict[str, str] = {"0": "DL", "1": "UL"}
    for case_arg in args.case:
        if "=" not in case_arg:
            parser.error(f"invalid --case {case_arg!r}; expected CASE_NAME=directory")
        case_name, case_dir_text = case_arg.split("=", 1)
        case_dir = Path(case_dir_text)
        mapping = read_csv(case_dir / "logs/flow-map.csv")
        packet_metrics = read_csv(case_dir / "analysis/ue_packet_metrics.csv")
        grants = read_csv(case_dir / "analysis/ue_grants.csv")
        demand = read_csv(case_dir / "logs/mac-demand.csv")

        metric_by_flow = {row["flow_id"]: row for row in packet_metrics}
        mapping_by_flow = {row["flow_id"]: row for row in mapping}
        if set(metric_by_flow) != set(mapping_by_flow):
            raise ValueError(f"{case_name}: packet metrics and configured flow IDs differ")
        ue_lookup = {(row["rnti_at_end"], row["direction"]): row
                     for row in mapping if row.get("rnti_at_end")}
        grant_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for grant in grants:
            meta = ue_lookup.get((grant["rnti"], grant["direction"]))
            if meta is None:
                unmatched_grants.append({
                    "case": case_name, "direction": grant["direction"],
                    "rnti": grant["rnti"], "simulation_time_ns": grant["simulation_time_ns"],
                    "allocated_prb": grant["allocated_prb"], "tb_size_bytes": grant["tb_size_bytes"],
                })
                continue
            grant_groups[(meta["ue_index"], meta["direction"])].append(grant)

        demand_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for sample in demand:
            direction = demand_codes.get(sample["direction"])
            meta = ue_lookup.get((sample["rnti"], direction or ""))
            if meta is not None:
                demand_groups[(meta["ue_index"], direction)].append(sample)

        for flow_id, meta in mapping_by_flow.items():
            metric = metric_by_flow[flow_id]
            key = (meta["ue_index"], meta["direction"])
            ue_grants = grant_groups[key]
            samples = demand_groups[key]
            buffers = [int(row["buffer_bytes"]) for row in samples]
            cqi = [int(row["cqi"]) for row in samples]
            rates = [float(row["achievable_rate_mbps"]) for row in samples]
            throughputs = [float(row["actual_throughput_mbps"]) for row in samples]
            tx = int(metric["tx_unique_packets"])
            rx = int(metric["rx_unique_packets"])
            summaries.append({
                "case": case_name, "ue_index": meta["ue_index"], "direction": meta["direction"],
                "rnti": meta["rnti_at_end"], "configured_rate_bps": int(meta["configured_rate_bps"]),
                "generated_rate_bps": metric["generated_rate_bps"],
                "delivered_goodput_bps": metric["delivered_goodput_bps"],
                "tx_unique_packets": tx, "rx_unique_packets": rx,
                "missing_by_sink_stop_packets": metric["missing_by_sink_stop_packets"],
                "received_delay_n": metric["received_delay_n"],
                "p95_delay_ns": metric["p95_delay_ns"], "p99_delay_ns": metric["p99_delay_ns"],
                "grant_count": len(ue_grants),
                "grant_allocated_prb_sum": sum(int(row["allocated_prb"]) for row in ue_grants),
                "grant_tb_size_bytes_sum": sum(int(row["tb_size_bytes"]) for row in ue_grants),
                "demand_sample_count": len(samples),
                "demand_buffer_mean_bytes": statistics.fmean(buffers) if buffers else "",
                "demand_buffer_max_bytes": max(buffers) if buffers else "",
                "demand_buffer_nonempty_fraction": sum(value > 0 for value in buffers) / len(buffers) if buffers else "",
                "demand_cqi_mean": statistics.fmean(cqi) if cqi else "",
                "demand_achievable_rate_mean_mbps": statistics.fmean(rates) if rates else "",
                "demand_actual_throughput_mean_mbps": statistics.fmean(throughputs) if throughputs else "",
            })

    columns = list(summaries[0]) if summaries else []
    write_csv(args.output_dir / "per-ue-load-calibration.csv", summaries, columns)
    write_csv(args.output_dir / "unmatched-grants.csv", unmatched_grants,
              ["case", "direction", "rnti", "simulation_time_ns", "allocated_prb", "tb_size_bytes"])
    (args.output_dir / "summary.json").write_text(json.dumps({
        "cases": [arg.split("=", 1)[0] for arg in args.case],
        "flow_rows": len(summaries),
        "unmatched_grant_rows": len(unmatched_grants),
        "mac_demand_direction_code_mapping": demand_codes,
        "metric_semantics": {
            "missing_by_sink_stop_packets": "generated unique TX packets without a matched RX by sink stop; not classified as physical-layer loss",
            "grant_allocated_prb_sum": "sum of applied grant PRB counts; not airtime or unique spectrum bandwidth",
            "unmatched_grants": "retained separately because applied-grant RNTI did not match per-UE end-of-run mapping",
        },
    }, indent=2) + "\n")
    print(f"flow_rows={len(summaries)} unmatched_grant_rows={len(unmatched_grants)}")


if __name__ == "__main__":
    main()
