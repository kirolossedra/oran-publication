#!/usr/bin/env python3
"""Analyze per-packet ns-3 UDP telemetry and export packet/grant/radio CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import yaml

EVENT_RE = re.compile(r"^PACKET_(TX|RX),")
GRANT_RE = re.compile(r"^APPLIED_GRANT,")
RADIO_RE = re.compile(r"^RADIO_MOBILITY_TRACE,")


def nearest_rank(values: list[int], quantile: float) -> int | None:
    """Nearest-rank empirical quantile, rank=ceil(q*n), one-based."""
    if not values:
        return None
    if not 0 < quantile <= 1:
        raise ValueError("quantile must be in (0, 1]")
    ordered = sorted(values)
    return ordered[math.ceil(quantile * len(ordered)) - 1]


def endpoint_key(source_ip: str, source_port: str, destination_ip: str, destination_port: str):
    return source_ip, int(source_port), destination_ip, int(destination_port)


def parse_stdout(path: Path):
    tx_events, rx_events, grants, radio = [], [], [], []
    for line in path.read_text().splitlines():
        if EVENT_RE.match(line):
            fields = line.split(",")
            kind = fields[0]
            event = {
                "event_time_ns": int(fields[1]),
                "sequence": int(fields[2]),
                "tx_time_ns": int(fields[3]),
                "payload_bytes": int(fields[4]),
                "source_ip": fields[5],
                "source_port": int(fields[6]),
                "destination_ip": fields[7],
                "destination_port": int(fields[8]),
            }
            (tx_events if kind == "PACKET_TX" else rx_events).append(event)
        elif GRANT_RE.match(line):
            f = line.split(",")
            grants.append({
                "simulation_time_ns": int(f[1]), "direction": f[2], "rnti": int(f[3]),
                "frame": int(f[4]), "subframe": int(f[5]), "slot": int(f[6]),
                "symbol_start": int(f[7]), "symbol_count": int(f[8]), "bwp_id": int(f[9]),
                "allocated_rbg": int(f[10]), "rb_per_rbg": int(f[11]),
                "allocated_prb": int(f[12]), "mcs": int(f[13]), "tb_size_bytes": int(f[14]),
                "ndi": int(f[15]), "rv": int(f[16]), "harq_id": int(f[17]),
                "rbg_bitmap": f[18],
            })
        elif RADIO_RE.match(line) and len(radio) == 0:
            radio.append({"header": line.split(",")[1:]})
        elif line.startswith("RADIO_MOBILITY_TRACE,"):
            radio.append({"row": line.split(",")[1:]})
    return tx_events, rx_events, grants, radio


def analyze_events(tx_events, rx_events, flow_rows, common):
    by_endpoint = {}
    wildcard_by_endpoint = {}
    flow_meta = {}
    for row in flow_rows:
        ep = endpoint_key(row["source_ip"], row["source_port"],
                          row["destination_ip"], row["destination_port"])
        if ep in by_endpoint:
            raise ValueError(f"duplicate flow endpoint mapping: {ep}")
        by_endpoint[ep] = row
        wildcard_by_endpoint[endpoint_key("0.0.0.0", row["source_port"],
                                           row["destination_ip"], row["destination_port"])] = row
        flow_meta[row["flow_id"]] = row

    def mapped_events(events, label):
        result = defaultdict(list)
        for event in events:
            ep = endpoint_key(event["source_ip"], event["source_port"],
                              event["destination_ip"], event["destination_port"])
            row = by_endpoint.get(ep)
            if row is None and label == "TX" and event["source_ip"] == "0.0.0.0":
                row = wildcard_by_endpoint.get(ep)
            if row is None:
                raise ValueError(f"{label} packet has no configured FlowId mapping: {ep}")
            result[row["flow_id"]].append(event)
        return result

    tx_by_flow = mapped_events(tx_events, "TX")
    rx_by_flow = mapped_events(rx_events, "RX")
    packet_rows, metrics = [], []
    flow_ids = set(flow_meta) | set(tx_by_flow) | set(rx_by_flow)
    for flow_id in sorted(flow_ids, key=int):
        meta = flow_meta[flow_id]
        txs = tx_by_flow[flow_id]
        rxs = rx_by_flow[flow_id]
        tx_index = defaultdict(list)
        rx_index = defaultdict(list)
        for e in txs:
            tx_index[e["sequence"]].append(e)
        for e in rxs:
            rx_index[e["sequence"]].append(e)

        duplicate_tx = sum(max(0, len(v) - 1) for v in tx_index.values())
        duplicate_rx = sum(max(0, len(v) - 1) for v in rx_index.values())
        unique_tx = {seq: vals[0] for seq, vals in tx_index.items()}
        unique_rx = {seq: vals[0] for seq, vals in rx_index.items()}
        tx_sequences = set(unique_tx)
        rx_sequences = set(unique_rx)
        missing = tx_sequences - rx_sequences
        unmatched = rx_sequences - tx_sequences
        ordered_rx = sorted((e["event_time_ns"], seq) for seq, e in unique_rx.items())
        high_seq, reordered = -1, 0
        for _, seq in ordered_rx:
            if seq < high_seq:
                reordered += 1
            high_seq = max(high_seq, seq)

        delays = []
        drained = 0
        source_stop_ns = int(float(meta["source_stop_s"]) * 1e9)
        for seq in sorted(tx_sequences):
            tx = unique_tx[seq]
            rx = unique_rx.get(seq)
            status = "missing_by_sink_stop" if rx is None else "delivered"
            delay_ns = ""
            rx_time_ns = ""
            if rx is not None:
                delay_ns = rx["event_time_ns"] - tx["tx_time_ns"]
                rx_time_ns = rx["event_time_ns"]
                if delay_ns < 0:
                    status = "invalid_negative_delay"
                else:
                    delays.append(delay_ns)
                if rx["event_time_ns"] > source_stop_ns:
                    drained += 1
            packet_rows.append({
                "flow_id": flow_id, "ue_index": meta["ue_index"],
                "direction": meta["direction"], "rnti": meta.get("rnti_at_end", ""),
                "sequence": seq, "tx_time_ns": tx["tx_time_ns"],
                "rx_time_ns": rx_time_ns, "payload_bytes": tx["payload_bytes"],
                "delay_ns": delay_ns, "status": status,
            })
        for seq in sorted(rx_sequences - tx_sequences):
            rx = unique_rx[seq]
            packet_rows.append({
                "flow_id": flow_id, "ue_index": meta["ue_index"],
                "direction": meta["direction"], "rnti": meta.get("rnti_at_end", ""),
                "sequence": seq, "tx_time_ns": "", "rx_time_ns": rx["event_time_ns"],
                "payload_bytes": rx["payload_bytes"], "delay_ns": "",
                "status": "unmatched_rx",
            })

        payload_tx = sum(e["payload_bytes"] for e in unique_tx.values())
        payload_rx = sum(unique_rx[s]["payload_bytes"] for s in tx_sequences & rx_sequences)
        window_s = float(meta["source_stop_s"]) - float(meta["source_start_s"])
        metrics.append({
            "flow_id": flow_id, "ue_index": meta["ue_index"],
            "direction": meta["direction"], "rnti": meta.get("rnti_at_end", ""),
            "configured_rate_bps": meta["configured_rate_bps"],
            # Configured application offer; generated_rate below measures actual
            # application payload emitted over the configured source interval.
            "offered_rate_bps": meta["configured_rate_bps"],
            "source_start_s": meta["source_start_s"], "source_stop_s": meta["source_stop_s"],
            "sink_stop_s": meta["sink_stop_s"], "tx_unique_packets": len(unique_tx),
            "rx_unique_packets": len(tx_sequences & rx_sequences),
            "duplicate_tx_packets": duplicate_tx, "duplicate_rx_packets": duplicate_rx,
            "unmatched_rx_packets": len(unmatched), "missing_by_sink_stop_packets": len(missing),
            "reordered_rx_packets": reordered, "drained_rx_packets": drained,
            "tx_payload_bytes": payload_tx, "rx_payload_bytes": payload_rx,
            "generated_rate_bps": payload_tx * 8 / window_s if window_s > 0 else "",
            "delivered_goodput_bps": payload_rx * 8 / window_s if window_s > 0 else "",
            "received_delay_n": len(delays),
            "p50_delay_ns": nearest_rank(delays, .50),
            "p95_delay_ns": nearest_rank(delays, .95),
            "p99_delay_ns": nearest_rank(delays, .99),
            "quantile_method": "nearest-rank ceil(q*n), 1-based; received unique packet IDs",
        })
    return packet_rows, metrics


def write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not columns:
        path.write_text("")
        return
    fields = columns or list(rows[0])
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True, help="map_g1_udp_flows.py CSV")
    parser.add_argument("--config", type=Path, required=True, help="effective run YAML")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    with args.mapping.open(newline="") as stream:
        mapping = list(csv.DictReader(stream))
    with args.config.open() as stream:
        config = yaml.safe_load(stream)
    tx, rx, grants, radio = parse_stdout(args.stdout)
    packets, metrics = analyze_events(tx, rx, mapping, config["common"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "packets.csv", packets,
              ["flow_id", "ue_index", "direction", "rnti", "sequence", "tx_time_ns",
               "rx_time_ns", "payload_bytes", "delay_ns", "status"])
    write_csv(args.output_dir / "ue_packet_metrics.csv", metrics)

    rnti_map = {(row.get("rnti_at_end", ""), row["direction"]): row for row in mapping}
    enriched_grants = []
    for grant in grants:
        meta = rnti_map.get((str(grant["rnti"]), grant["direction"]), {})
        enriched_grants.append({"ue_index": meta.get("ue_index", ""), "flow_id": meta.get("flow_id", ""), **grant})
    grant_columns = ["ue_index", "flow_id", "simulation_time_ns", "direction", "rnti", "frame",
                     "subframe", "slot", "symbol_start", "symbol_count", "bwp_id", "allocated_rbg",
                     "rb_per_rbg", "allocated_prb", "mcs", "tb_size_bytes", "ndi", "rv", "harq_id",
                     "rbg_bitmap"]
    write_csv(args.output_dir / "ue_grants.csv", enriched_grants, grant_columns)

    radio_rows = []
    if radio:
        headers = radio[0]["header"]
        for item in radio[1:]:
            if "row" in item:
                radio_rows.append(dict(zip(headers, item["row"])))
        write_csv(args.output_dir / "ue_radio.csv", radio_rows, headers)
    else:
        write_csv(args.output_dir / "ue_radio.csv", [], ["time_s", "ue_index", "ue_node_id", "gnb_node_id", "rnti", "gnb_x_m", "gnb_y_m", "gnb_z_m", "ue_x_m", "ue_y_m", "ue_z_m", "condition"])
    (args.output_dir / "summary.json").write_text(json.dumps({"flows": metrics}, indent=2) + "\n")
    print(f"analyzed_flows={len(metrics)} tx_events={len(tx)} rx_events={len(rx)} grants={len(grants)}")


if __name__ == "__main__":
    main()
