#!/usr/bin/env python3
"""Compare per-UE decisions, applied grants and packet outcomes across stock policies."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml


DECISION_RE = re.compile(
    r"^Control step: (?P<step>\d+) \| (?P<direction>[01]) \| "
    r"RNTI=(?P<rnti>\d+), (?:PRBs|RBGs)=\[(?P<start>\d+)-(?P<end>\d+)\], "
    r"MCS=(?P<mcs>\d+)"
)
DIRECTIONS = {"0": "DL", "1": "UL"}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def decisions_by_ue(path: Path, flow_map: list[dict[str, str]]) -> tuple[dict, int]:
    rnti_map = {(row["rnti_at_end"], row["direction"]):
                (row["ue_index"], row["direction"]) for row in flow_map}
    counts: Counter = Counter()
    parsed = 0
    unmatched = 0
    for line in path.read_text(errors="replace").splitlines():
        match = DECISION_RE.match(line)
        if not match:
            continue
        parsed += 1
        key = rnti_map.get((match["rnti"], DIRECTIONS[match["direction"]]))
        if key is None:
            unmatched += 1
        else:
            counts[key] += 1
    return counts, unmatched


def policy(config_path: Path) -> str:
    with config_path.open() as stream:
        return yaml.safe_load(stream)["orchestrator"]["dapp_algo_ue_selection"]


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return ("number", float(value))
    if isinstance(value, str):
        try:
            return ("number", float(value))
        except ValueError:
            return value
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite nonempty output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    baseline_cfg_path = args.baseline / "effective-run-config.yaml"
    candidate_cfg_path = args.candidate / "effective-run-config.yaml"
    with baseline_cfg_path.open() as stream:
        baseline_cfg = yaml.safe_load(stream)
    with candidate_cfg_path.open() as stream:
        candidate_cfg = yaml.safe_load(stream)
    baseline_policy = policy(baseline_cfg_path)
    candidate_policy = policy(candidate_cfg_path)
    baseline_control = json.loads(json.dumps(baseline_cfg))
    candidate_control = json.loads(json.dumps(candidate_cfg))
    baseline_control["orchestrator"].pop("dapp_algo_ue_selection")
    candidate_control["orchestrator"].pop("dapp_algo_ue_selection")
    if normalize(baseline_control) != normalize(candidate_control):
        raise ValueError("paired effective configs differ outside dApp selector")
    if baseline_cfg["common"]["rngRun"] != candidate_cfg["common"]["rngRun"]:
        raise ValueError("paired effective configs have different RNG runs")

    base_map = load_csv(args.baseline / "logs/flow-map.csv")
    cand_map = load_csv(args.candidate / "logs/flow-map.csv")
    base_metrics = load_csv(args.baseline / "analysis/ue_packet_metrics.csv")
    cand_metrics = load_csv(args.candidate / "analysis/ue_packet_metrics.csv")
    base_grants = load_csv(args.baseline / "analysis/ue_grants.csv")
    cand_grants = load_csv(args.candidate / "analysis/ue_grants.csv")
    base_ids = {(row["ue_index"], row["direction"]) for row in base_map}
    cand_ids = {(row["ue_index"], row["direction"]) for row in cand_map}
    if base_ids != cand_ids or len(base_ids) != 12:
        raise ValueError("paired arm does not contain the same 12 per-UE UL/DL flows")
    for label, mapping in (("baseline", base_map), ("candidate", cand_map)):
        if any(row["flowmonitor_tx_event_counter_match"] != "true"
               or row["flowmonitor_rx_event_counter_match"] != "true" for row in mapping):
            raise ValueError(f"{label}: packet-event counters do not reconcile with FlowMonitor")

    def metric_map(rows):
        result = {}
        for row in rows:
            key = (row["ue_index"], row["direction"])
            if key in result:
                raise ValueError(f"duplicate flow metrics for {key}")
            result[key] = row
        return result

    def grant_summary(rows):
        summary = defaultdict(lambda: {"count": 0, "prb_sum": 0, "tb_sum": 0})
        unmatched = Counter()
        for row in rows:
            if not row["ue_index"]:
                unmatched[row["direction"]] += 1
                continue
            item = summary[(row["ue_index"], row["direction"])]
            item["count"] += 1
            item["prb_sum"] += int(row["allocated_prb"])
            item["tb_sum"] += int(row["tb_size_bytes"])
        return summary, unmatched

    base_decisions, base_unmatched_decisions = decisions_by_ue(
        args.baseline / "logs/dapp-decisions.log", base_map)
    cand_decisions, cand_unmatched_decisions = decisions_by_ue(
        args.candidate / "logs/dapp-decisions.log", cand_map)
    base_metrics = metric_map(base_metrics)
    cand_metrics = metric_map(cand_metrics)
    base_grant_summary, base_unmatched_grants = grant_summary(base_grants)
    cand_grant_summary, cand_unmatched_grants = grant_summary(cand_grants)

    rows = []
    changed_actual = False
    for ue, direction in sorted(base_ids, key=lambda key: (int(key[0]), key[1])):
        key = (ue, direction)
        base = base_metrics[key]
        candidate = cand_metrics[key]
        bg = base_grant_summary[key]
        cg = cand_grant_summary[key]
        bd = base_decisions[key]
        cd = cand_decisions[key]
        if (bg["count"], bg["prb_sum"], bg["tb_sum"]) != (cg["count"], cg["prb_sum"], cg["tb_sum"]):
            changed_actual = True
        rows.append({
            "ue_index": ue, "direction": direction,
            "baseline_policy": baseline_policy, "candidate_policy": candidate_policy,
            "baseline_dapp_decisions": bd, "candidate_dapp_decisions": cd,
            "baseline_applied_grants": bg["count"], "candidate_applied_grants": cg["count"],
            "baseline_applied_prb_sum": bg["prb_sum"], "candidate_applied_prb_sum": cg["prb_sum"],
            "baseline_tb_bytes_sum": bg["tb_sum"], "candidate_tb_bytes_sum": cg["tb_sum"],
            "baseline_tx_unique_packets": base["tx_unique_packets"], "candidate_tx_unique_packets": candidate["tx_unique_packets"],
            "baseline_rx_unique_packets": base["rx_unique_packets"], "candidate_rx_unique_packets": candidate["rx_unique_packets"],
            "baseline_missing_by_sink_stop": base["missing_by_sink_stop_packets"], "candidate_missing_by_sink_stop": candidate["missing_by_sink_stop_packets"],
            "baseline_goodput_bps": base["delivered_goodput_bps"], "candidate_goodput_bps": candidate["delivered_goodput_bps"],
            "baseline_received_delay_n": base["received_delay_n"], "candidate_received_delay_n": candidate["received_delay_n"],
            "baseline_p95_delay_ns": base["p95_delay_ns"], "candidate_p95_delay_ns": candidate["p95_delay_ns"],
            "baseline_p99_delay_ns": base["p99_delay_ns"], "candidate_p99_delay_ns": candidate["p99_delay_ns"],
        })
    columns = list(rows[0])
    with (args.output_dir / "per-ue-policy-comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    base_grants_total = sum(value["count"] for value in base_grant_summary.values()) + sum(base_unmatched_grants.values())
    cand_grants_total = sum(value["count"] for value in cand_grant_summary.values()) + sum(cand_unmatched_grants.values())
    summary = {
        "baseline_policy": baseline_policy,
        "candidate_policy": candidate_policy,
        "seed": baseline_cfg["common"]["rngRun"],
        "flow_rows": len(rows),
        "paired_effective_configs_equal_outside_dapp_policy": True,
        "baseline_parsed_dapp_decisions": sum(base_decisions.values()) + base_unmatched_decisions,
        "candidate_parsed_dapp_decisions": sum(cand_decisions.values()) + cand_unmatched_decisions,
        "baseline_decision_rows_with_unmapped_rnti": base_unmatched_decisions,
        "candidate_decision_rows_with_unmapped_rnti": cand_unmatched_decisions,
        "baseline_applied_grants": base_grants_total,
        "candidate_applied_grants": cand_grants_total,
        "baseline_grants_with_unmapped_rnti": dict(base_unmatched_grants),
        "candidate_grants_with_unmapped_rnti": dict(cand_unmatched_grants),
        "applied_grant_distribution_changed": changed_actual,
        "decision_logging_changed": base_decisions != cand_decisions,
        "interpretation_boundary": "One matched seed is an engineering probe; packet tails are diagnostic and not inferential.",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"flows={len(rows)} baseline_grants={base_grants_total} candidate_grants={cand_grants_total} applied_grant_distribution_changed={changed_actual}")


if __name__ == "__main__":
    main()
