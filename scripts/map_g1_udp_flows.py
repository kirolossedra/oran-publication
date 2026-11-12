#!/usr/bin/env python3
"""Join RA-ENG-003 C++ per-UE traffic rows to ns-3 FlowMonitor FlowIds."""

from __future__ import annotations

import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--flowstats", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-counter-differences", action="store_true",
                        help="record source/sink vs FlowMonitor differences instead of failing")
    args = parser.parse_args()

    classifiers = {}
    root = ET.parse(args.flowstats).getroot()
    for item in root.findall(".//Ipv4FlowClassifier/Flow"):
        classifiers[(item.get("sourceAddress"), item.get("destinationAddress"),
                     int(item.get("sourcePort", "0")), int(item.get("destinationPort", "0")),
                     int(item.get("protocol", "0")))] = int(item.get("flowId", "0"))
    flow_stats = {
        int(item.get("flowId", "0")): item.attrib
        for item in root.findall(".//FlowStats/Flow")
    }

    rows = []
    for line in args.stdout.read_text().splitlines():
        if line.startswith("UE_TRAFFIC_CONFIG,"):
            fields = line.split(",")
            _, direction, ue_index, ue_ip, rnti, remote_ip, port, rate, size, start, stop, sink_stop = fields
            port = int(port)
            if direction == "DL":
                # ns-3 chooses the ephemeral source port; match the stable destination tuple.
                candidates = [(k, value) for k, value in classifiers.items()
                              if k[1] == ue_ip and k[3] == port and k[4] == 17]
            else:
                candidates = [(k, value) for k, value in classifiers.items()
                              if k[0] == ue_ip and k[3] == port and k[4] == 17]
            if len(candidates) != 1:
                raise SystemExit(f"expected one FlowId for {direction} UE {ue_index} port {port}; found {len(candidates)}")
            flow_id = candidates[0][1]
            flow_tuple = next(k for k, value in classifiers.items() if value == flow_id)
            if flow_id not in flow_stats:
                raise SystemExit(f"FlowMonitor has no stats for FlowId {flow_id}")
            rows.append({"ue_index": ue_index, "direction": direction, "ue_ip": ue_ip,
                         "rnti_at_setup": rnti, "flow_id": flow_id, "udp_port": port,
                         "source_ip": flow_tuple[0], "source_port": flow_tuple[2],
                         "destination_ip": flow_tuple[1], "destination_port": flow_tuple[3],
                         "configured_rate_bps": rate, "payload_bytes": size,
                         "source_start_s": start, "source_stop_s": stop, "sink_stop_s": sink_stop,
                         "flowmonitor_tx_packets": flow_stats[flow_id].get("txPackets", "0"),
                         "flowmonitor_rx_packets": flow_stats[flow_id].get("rxPackets", "0")})

    results = {}
    for line in args.stdout.read_text().splitlines():
        if line.startswith("UE_TRAFFIC_RESULT,"):
            fields = line.split(",")
            _, direction, ue_index, ue_ip, rnti, remote_ip, port, tx_packets, tx_bytes, rx_packets, rx_bytes = fields
            results[(direction, int(ue_index), int(port))] = (rnti, tx_packets, tx_bytes, rx_packets, rx_bytes)
    for row in rows:
        key = (row["direction"], int(row["ue_index"]), int(row["udp_port"]))
        if key not in results:
            raise SystemExit(f"missing C++ event counters for {key}")
        rnti, tx_packets, tx_bytes, rx_packets, rx_bytes = results[key]
        stats = flow_stats[int(row["flow_id"])]
        flow_tx = int(stats.get("txPackets", "0"))
        flow_rx = int(stats.get("rxPackets", "0"))
        tx_match = flow_tx == int(tx_packets)
        rx_match = flow_rx == int(rx_packets)
        row["flowmonitor_tx_event_counter_match"] = str(tx_match).lower()
        row["flowmonitor_rx_event_counter_match"] = str(rx_match).lower()
        if not tx_match and not args.allow_counter_differences:
            raise SystemExit(f"FlowId {row['flow_id']} TX packet count disagrees with source event counter")
        if not rx_match and not args.allow_counter_differences:
            raise SystemExit(f"FlowId {row['flow_id']} RX packet count disagrees with sink event counter")
        row.update({"rnti_at_end": rnti, "source_tx_packets": tx_packets,
                    "source_tx_payload_bytes": tx_bytes, "sink_rx_packets": rx_packets,
                    "sink_rx_payload_bytes": rx_bytes})

    if not rows:
        raise SystemExit("no UE_TRAFFIC_CONFIG rows found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
