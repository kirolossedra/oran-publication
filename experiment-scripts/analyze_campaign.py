#!/usr/bin/env python3
"""Summarize preserved G1 run directories; packets are observations, seeds are replicates."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import argparse

from run_campaign import outcome_source_hashes, has_data_rows, SPEC_PATH


ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "configs/experiment.json").read_text())
CAMPAIGN = ROOT / "simulator/runs" / SPEC["campaign_id"]
OUT = ROOT / "results" / SPEC["campaign_id"]
FACTORS = ("channel", "mobility", "load", "policy")
T95_T_CRIT = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
              7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    pos = (len(xs) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def mean_sd_ci(values: list[float]):
    if not values:
        return (None, None, None, None, 0)
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else None
    t = T95_T_CRIT.get(len(values) - 1, 1.96) if len(values) > 1 else None
    margin = t * sd / math.sqrt(len(values)) if sd is not None else None
    return mean, sd, mean - margin if margin is not None else None, mean + margin if margin is not None else None, len(values)


def policy_channel_difference_in_differences(los_round_robin: float, los_topk: float,
                                             nlos_round_robin: float, nlos_topk: float) -> float:
    """Return (TopKCqi-RoundRobin) under UE6 NLOS minus the same effect under LOS."""
    return (nlos_topk - nlos_round_robin) - (los_topk - los_round_robin)


def build_policy_channel_interactions(ue_rows: list[dict], grant_rows: list[dict]):
    """Create matched-seed policy-by-channel interaction rows and seed-level summaries."""
    ue_lookup = {(r["channel"], r["mobility"], r["load"], r["policy"], int(r["seed"],),
                  r["direction"], int(r["ue_index"])): r for r in ue_rows}
    grant_lookup = {(r["channel"], r["mobility"], r["load"], r["policy"], int(r["seed"],),
                     r["direction"], int(r["ue_index"])): r for r in grant_rows}
    metrics = ("rx_goodput_bps", "pdr", "mean_latency_ms", "p95_latency_ms", "p99_latency_ms")
    seed_rows = []
    for mobility, load, seed, direction, ue in sorted({
        (r["mobility"], r["load"], int(r["seed"]), r["direction"], int(r["ue_index"])) for r in ue_rows
    }):
        key = lambda channel, policy: (channel, mobility, load, policy, seed, direction, ue)
        quartet = {name: ue_lookup.get(key(channel, policy))
                   for name, channel, policy in (
                       ("los_rr", "all-los", "RoundRobin"), ("los_topk", "all-los", "TopKCqi"),
                       ("nlos_rr", "ue6-nlos", "RoundRobin"), ("nlos_topk", "ue6-nlos", "TopKCqi"))}
        if any(row is None for row in quartet.values()):
            continue
        base = {"mobility": mobility, "load": load, "seed": seed, "direction": direction, "ue_index": ue,
                "contrast": "(TopKCqi-RoundRobin)_UE6-NLOS - (TopKCqi-RoundRobin)_all-LOS"}
        for metric in metrics:
            values = {name: row.get(metric) for name, row in quartet.items()}
            if any(value is None for value in values.values()):
                continue
            effect_los = float(values["los_topk"]) - float(values["los_rr"])
            effect_nlos = float(values["nlos_topk"]) - float(values["nlos_rr"])
            adequacy = "not-applicable"
            if metric == "p99_latency_ms":
                min_n = min(int(row["received_latency_n"]) for row in quartet.values())
                adequacy = "adequate-by-1000-sample-rule" if min_n >= 1000 else "inadequate-by-1000-sample-rule"
            seed_rows.append({**base, "metric": metric, "policy_effect_all_los": effect_los,
                              "policy_effect_ue6_nlos": effect_nlos,
                              "policy_effect_difference_in_differences": policy_channel_difference_in_differences(
                                  float(values["los_rr"]), float(values["los_topk"]),
                                  float(values["nlos_rr"]), float(values["nlos_topk"])),
                              "p99_interaction_adequacy": adequacy})
        grant_quartet = {name: grant_lookup.get(key(channel, policy))
                         for name, channel, policy in (
                             ("los_rr", "all-los", "RoundRobin"), ("los_topk", "all-los", "TopKCqi"),
                             ("nlos_rr", "ue6-nlos", "RoundRobin"), ("nlos_topk", "ue6-nlos", "TopKCqi"))}
        if all(row is not None for row in grant_quartet.values()):
            values = {name: int(row["prb_symbols"]) for name, row in grant_quartet.items()}
            effect_los = values["los_topk"] - values["los_rr"]
            effect_nlos = values["nlos_topk"] - values["nlos_rr"]
            seed_rows.append({**base, "metric": "prb_symbols",
                              "policy_effect_all_los": effect_los,
                              "policy_effect_ue6_nlos": effect_nlos,
                              "policy_effect_difference_in_differences": effect_nlos - effect_los,
                              "p99_interaction_adequacy": "not-applicable"})
    grouped = {}
    for row in seed_rows:
        key = (row["mobility"], row["load"], row["direction"], row["ue_index"], row["metric"])
        grouped.setdefault(key, []).append(row)
    summaries = []
    for key, rows in sorted(grouped.items()):
        values = [float(row["policy_effect_difference_in_differences"]) for row in rows]
        mean, sd, low, high, n = mean_sd_ci(values)
        summaries.append({**dict(zip(("mobility", "load", "direction", "ue_index", "metric"), key)),
                          "paired_seed_n": n, "mean_policy_effect_difference_in_differences": mean,
                          "sd_across_seed_interactions": sd, "ci95_low": low, "ci95_high": high,
                          "adequate_p99_seed_n": sum(row["p99_interaction_adequacy"] == "adequate-by-1000-sample-rule" for row in rows),
                          "inadequate_p99_seed_n": sum(row["p99_interaction_adequacy"] == "inadequate-by-1000-sample-rule" for row in rows)})
    return seed_rows, summaries


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cell_factors(attempt: Path) -> dict:
    meta = json.loads((attempt / "cell.json").read_text())
    return meta


def unique_planned_cells(base: list[dict], extension: list[dict]) -> dict[str, dict]:
    """Directional extension may repeat cells; each experiment ID is unique."""
    planned = {}
    for cell in [*base, *extension]:
        cid = cell["cell_id"]
        if cid in planned and planned[cid] != cell:
            raise ValueError(f"Conflicting duplicate matrix cell: {cid}")
        planned[cid] = cell
    return planned


def main():
    global CAMPAIGN, OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", type=Path, default=CAMPAIGN)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    CAMPAIGN = args.campaign_root.absolute()
    OUT = args.output_dir.resolve()
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(f"refusing to overwrite nonempty analysis output directory: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    attempt_dirs = sorted(CAMPAIGN.glob("cells/*/attempt-*"))
    audit, ue_rows, grant_rows, demand_rows = [], [], [], []
    expected_source_hashes = outcome_source_hashes()
    primary_attempt = {}
    validation_reasons = {}
    for candidate in attempt_dirs:
        status = candidate / "exit-status.txt"
        if not status.exists():
            validation_reasons[candidate] = "missing exit-status.txt; interrupted or status unavailable"
            continue
        status_value = status.read_text().strip()
        if status_value != "0":
            validation_reasons[candidate] = f"process exit status {status_value}"
            continue
        try:
            metadata = json.loads((candidate / "run-metadata.json").read_text())
            if metadata.get("packet_measurement_schema") != "serialized-app-header-v1":
                validation_reasons[candidate] = "packet measurement schema missing or unsupported"
                continue
            if metadata.get("source_sha256") != expected_source_hashes:
                validation_reasons[candidate] = "source SHA-256 differs from current campaign source"
                continue  # do not pool old and corrected policy results
            if not (candidate / "logs/kpi.json").is_file():
                validation_reasons[candidate] = "KPI output missing"
                continue
            if not has_data_rows(candidate / "logs/packet-events.csv",
                                 {"event", "time_ns", "ue_index", "direction", "sequence", "tx_time_ns", "bytes"}):
                validation_reasons[candidate] = "packet-event trace missing required header or data rows"
                continue
            if not has_data_rows(candidate / "logs/mac-grants.csv",
                                 {"time_ns", "rnti", "direction", "rbg_count", "mcs"}):
                validation_reasons[candidate] = "MAC-grant trace missing required header or data rows"
                continue
            if not has_data_rows(candidate / "logs/mac-demand.csv",
                                 {"time_ns", "rnti", "direction", "buffer_bytes", "cqi"}):
                validation_reasons[candidate] = "MAC-demand trace missing required header or data rows"
                continue
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            validation_reasons[candidate] = f"required metadata unreadable: {type(exc).__name__}: {exc}"
            continue
        validation_reasons[candidate] = "valid complete attempt"
        cell_id = candidate.parent.name
        current = primary_attempt.get(cell_id)
        old_num = int(current.name.split("-", 1)[1]) if current else -1
        next_num = int(candidate.name.split("-", 1)[1])
        if next_num > old_num:
            primary_attempt[cell_id] = candidate
    source_paths = [
        SPEC_PATH,
        Path(__file__).resolve().with_name("run_campaign.py"),
        Path(__file__).resolve(),
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_application/iboran-application.cc",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_application/iboran-application.h",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_mac_scheduler/iboran-nr-mac-scheduler.cc",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_ran_environment/iboran-nr-environment.cc",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_ran_environment/iboran-ran-common.cc",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_ran_environment/iboran-ran-params.cc",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_ran_environment/iboran-ran-params.h",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/utils/config_store.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_campaign/iboran_orchestrator.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_controller/iboran_dapp.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_controller/iboran_dapp_mac_scheduler.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_round_robin.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_top_k.py",
        ROOT / "simulator/ns-3.48/contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection.py",
    ]
    (OUT / "source-sha256.txt").write_text("".join(
        f"{sha256(path)}  {path.relative_to(ROOT)}\n" for path in source_paths if path.exists()
    ))
    for attempt in attempt_dirs:
        inventory = attempt / "artifact-sha256.txt"
        if not inventory.exists():
            files = sorted(p for p in attempt.rglob("*") if p.is_file() and p != inventory)
            inventory.write_text("".join(
                f"{sha256(path)}  {path.relative_to(attempt)}\n" for path in files
            ))
    for attempt in attempt_dirs:
        status_file = attempt / "exit-status.txt"
        status = int(status_file.read_text().strip()) if status_file.exists() else None
        cell = cell_factors(attempt)
        kpi = attempt / "logs/kpi.json"
        packet_path = attempt / "logs/packet-events.csv"
        grants_path = attempt / "logs/mac-grants.csv"
        success = status == 0 and kpi.exists()
        demand_file = attempt / "logs/mac-demand.csv"
        try:
            attempt_meta = json.loads((attempt / "run-metadata.json").read_text())
            revision_match = attempt_meta.get("source_sha256") == expected_source_hashes
        except (OSError, ValueError, json.JSONDecodeError):
            revision_match = False
        measurement_complete = (success and revision_match
            and has_data_rows(packet_path, {"event", "time_ns", "ue_index", "direction", "sequence", "tx_time_ns", "bytes"})
            and has_data_rows(grants_path, {"time_ns", "rnti", "direction", "rbg_count", "mcs"})
            and has_data_rows(demand_file, {"time_ns", "rnti", "direction", "buffer_bytes", "cqi"}))
        selected_for_analysis = primary_attempt.get(attempt.parent.name) == attempt
        reason = validation_reasons.get(attempt, "not considered for analysis")
        exclusion_reason = "" if selected_for_analysis else (
            "valid attempt superseded by a higher-numbered complete attempt"
            if reason == "valid complete attempt" else reason)
        audit.append({**cell, "attempt": str(attempt.relative_to(ROOT)), "exit_status": status,
                      "has_kpi": kpi.exists(), "has_packet_events": packet_path.exists(),
                      "has_mac_grants": grants_path.exists(),
                      "has_mac_demand": (attempt / "logs/mac-demand.csv").exists(),
                      "successful": success, "matches_current_source": revision_match,
                      "measurement_complete": measurement_complete,
                      "selected_for_analysis": selected_for_analysis,
                      "exclusion_reason": exclusion_reason})
        if not selected_for_analysis:
            continue
        meta = json.loads((attempt / "run-metadata.json").read_text())
        config = json.loads("{}")
        import yaml
        config = yaml.safe_load((attempt / "logs/runConfig.yaml").read_text())
        sim_time = float(config["common"]["simTime"])
        drain = float(config["common"].get("receiverDrainTime", 0))
        observation_s = sim_time - 1.1 - drain - 1.1
        per_ue_rates = {
            "DL": config["common"].get("perUeDlBitRate", []),
            "UL": config["common"].get("perUeUlBitRate", []),
        }
        events = read_csv(packet_path)
        keyed: dict[tuple[int, str], dict] = {}
        last_rx_sequence = {}
        rnti_to_ue = {}
        for e in events:
            ue = int(e["ue_index"])
            direction = "DL" if int(e["direction"]) == 0 else "UL"
            seq = int(e["sequence"])
            rnti = int(e["rnti"])
            if rnti:
                rnti_to_ue[rnti] = ue
            group = keyed.setdefault((ue, direction), {"TX": {}, "RX": {}, "tx_events": 0,
                                                        "rx_events": 0, "tx_duplicates": 0,
                                                        "rx_duplicates": 0, "reordered": 0})
            if e["event"] == "TX":
                group["tx_events"] += 1
                if seq in group["TX"]:
                    group["tx_duplicates"] += 1
            if e["event"] == "RX":
                group["rx_events"] += 1
                k = (ue, direction)
                if k in last_rx_sequence and seq < last_rx_sequence[k]:
                    group["reordered"] += 1
                last_rx_sequence[k] = max(seq, last_rx_sequence.get(k, seq))
                if seq in group["RX"]:
                    group["rx_duplicates"] += 1
            group[e["event"]].setdefault(seq, e)
        for (ue, direction), group in sorted(keyed.items()):
            tx, rx = group["TX"], group["RX"]
            latencies = []
            for seq, rec in rx.items():
                if seq in tx:
                    latencies.append((int(rec["time_ns"]) - int(tx[seq]["time_ns"])) / 1e6)
            tx_bytes = sum(int(x["bytes"]) for x in tx.values())
            rx_bytes = sum(int(x["bytes"]) for x in rx.values())
            matched_rx_packets = len(set(tx) & set(rx))
            rx_without_tx = len(set(rx) - set(tx))
            losses = len(set(tx) - set(rx))
            n = len(latencies)
            row = {
                **cell, "ue_index": ue, "direction": direction,
                "offered_bps_configured": per_ue_rates[direction][ue - 1] if len(per_ue_rates[direction]) >= ue else None,
                "tx_events": group["tx_events"], "tx_packets": len(tx),
                "tx_duplicate_events": group["tx_duplicates"],
                "rx_events": group["rx_events"], "rx_unique_packets": len(set(rx)),
                "rx_duplicate_events": group["rx_duplicates"], "rx_without_matching_tx": rx_without_tx,
                "matched_rx_packets": matched_rx_packets,
                "lost_or_unreceived_at_stop": losses,
                "reordered_rx_events": group["reordered"],
                "pdr": matched_rx_packets / len(tx) if tx else None,
                "tx_bytes": tx_bytes, "rx_bytes": rx_bytes,
                "application_tx_rate_bps": tx_bytes * 8 / observation_s if observation_s > 0 else None,
                "rx_goodput_bps": rx_bytes * 8 / observation_s if observation_s > 0 else None,
                "received_latency_n": n,
                "mean_latency_ms": statistics.mean(latencies) if latencies else None,
                "p50_latency_ms": quantile(latencies, .50), "p95_latency_ms": quantile(latencies, .95),
                "p99_latency_ms": quantile(latencies, .99),
                "p99_sample_adequacy": "exploratory-small-n" if n < 1000 else "at-least-1000-received",
                "latency_scope": "application one-way; includes modeled backhaul",
            }
            ue_rows.append(row)
        grant_acc = {}
        for grant in read_csv(grants_path):
            rnti = int(grant["rnti"])
            ue = rnti_to_ue.get(rnti)
            if ue is None:
                continue
            key = (ue, grant["direction"])
            agg = grant_acc.setdefault(key, {"grant_count": 0, "rbg_count": 0, "prb_count": 0,
                                               "prb_symbols": 0, "tbs_bytes": 0, "mcs": []})
            agg["grant_count"] += 1
            for name in ("rbg_count", "prb_count", "prb_symbols", "tbs_bytes"):
                agg[name] += int(grant[name])
            agg["mcs"].append(int(grant["mcs"]))
        for (ue, direction), agg in sorted(grant_acc.items()):
            grant_rows.append({**cell, "ue_index": ue, "direction": direction,
                               **{k: v for k, v in agg.items() if k != "mcs"},
                               "mean_mcs": statistics.mean(agg["mcs"]) if agg["mcs"] else None})
        demand_acc = {}
        for demand in read_csv(attempt / "logs/mac-demand.csv"):
            rnti = int(demand["rnti"])
            ue = rnti_to_ue.get(rnti)
            if ue is None:
                continue
            direction = "DL" if int(demand["direction"]) == 0 else "UL"
            agg = demand_acc.setdefault((ue, direction), {"buffer": [], "rate": [], "throughput": [], "cqi": []})
            agg["buffer"].append(int(demand["buffer_bytes"]))
            agg["cqi"].append(int(demand["cqi"]))
            # Early raw trace revisions used *_bps labels although the pinned
            # scheduler provides these values in Mbps; normalize to explicit Mbps.
            agg["rate"].append(float(demand.get("achievable_rate_mbps") or demand.get("achievable_rate_bps")))
            agg["throughput"].append(float(demand.get("actual_throughput_mbps") or demand.get("actual_throughput_bps")))
        for (ue, direction), agg in sorted(demand_acc.items()):
            demand_rows.append({**cell, "ue_index": ue, "direction": direction,
                                "demand_samples": len(agg["buffer"]),
                                "mean_queue_bytes": statistics.mean(agg["buffer"]),
                                "median_queue_bytes": statistics.median(agg["buffer"]),
                                "max_queue_bytes": max(agg["buffer"]),
                                "fraction_nonempty_queue": sum(x > 0 for x in agg["buffer"]) / len(agg["buffer"]),
                                "mean_achievable_rate_mbps": statistics.mean(agg["rate"]),
                                "mean_actual_throughput_mbps": statistics.mean(agg["throughput"]),
                                "mean_reported_cqi": statistics.mean(agg["cqi"]),
                                "cqi_samples": len(agg["cqi"])})

    # Validate that the intended link-state intervention and mobility are
    # visible in the simulator's per-second position/channel-state log.
    channel_audit = []
    for cell_id, attempt in primary_attempt.items():
        cell = cell_factors(attempt)
        snapshots = {}
        log_path = attempt / "execution.log"
        if log_path.exists():
            for line in log_path.read_text(errors="replace").splitlines():
                if not line.startswith("CHANNEL_STATE,"):
                    continue
                fields = dict(part.split("=", 1) for part in line.strip().split(",") if "=" in part)
                try:
                    ue = int(fields["ue_index"])
                    t = float(fields["time_s"])
                    position = tuple(float(x) for x in fields["ue_position_m"].split(":"))
                    snapshots.setdefault(ue, []).append((t, position, fields["condition"]))
                except (KeyError, ValueError):
                    continue
        expected_nlos = {6} if cell["channel"] == "ue6-nlos" else set()
        condition_mismatches = 0
        moving_ues = 0
        for ue in range(1, 7):
            samples = snapshots.get(ue, [])
            expected = "NLOS" if ue in expected_nlos else "LOS"
            condition_mismatches += sum(condition != expected for _, _, condition in samples)
            if len({position for _, position, _ in samples}) > 1:
                moving_ues += 1
        sample_total = sum(len(v) for v in snapshots.values())
        expected_moving = cell["mobility"] == "controlled-linear"
        channel_audit.append({
            **cell, "channel_state_samples": sample_total,
            "ue_count_with_channel_trace": len(snapshots),
            "condition_mismatch_samples": condition_mismatches,
            "ue_count_with_position_change": moving_ues,
            "expected_mobile": expected_moving,
            "channel_position_audit_pass": (len(snapshots) == 6 and sample_total >= 120
                                             and condition_mismatches == 0
                                             and ((moving_ues == 6) if expected_moving else moving_ues == 0)),
        })

    # Include zero-grant UE/direction pairs explicitly, then normalize each
    # user's PRB-symbol allocation by all observed applied grants in that run
    # and direction. This is a share among granted resources, not cell utilization.
    grant_keys = {(r["cell_id"], int(r["ue_index"]), r["direction"]) for r in grant_rows}
    for r in ue_rows:
        key = (r["cell_id"], int(r["ue_index"]), r["direction"])
        if key not in grant_keys:
            grant_rows.append({**{k: r[k] for k in (*FACTORS, "seed", "directions", "cell_id")},
                               "ue_index": int(r["ue_index"]), "direction": r["direction"],
                               "grant_count": 0, "rbg_count": 0, "prb_count": 0,
                               "prb_symbols": 0, "tbs_bytes": 0, "mean_mcs": None})
    totals = {}
    for r in grant_rows:
        key = (r["cell_id"], r["direction"])
        totals[key] = totals.get(key, 0) + int(r["prb_symbols"])
    for r in grant_rows:
        total = totals.get((r["cell_id"], r["direction"]), 0)
        r["prb_symbol_share"] = int(r["prb_symbols"]) / total if total else None
        r["received_resource_denominator_prb_symbols"] = total

    grant_lookup = {(r["cell_id"], int(r["ue_index"]), r["direction"]): r for r in grant_rows}
    peer_seed_rows = []
    metric_sources = {
        "rx_goodput_bps": {(r["cell_id"], int(r["ue_index"]), r["direction"]): r.get("rx_goodput_bps") for r in ue_rows},
        "pdr": {(r["cell_id"], int(r["ue_index"]), r["direction"]): r.get("pdr") for r in ue_rows},
        "p95_latency_ms": {(r["cell_id"], int(r["ue_index"]), r["direction"]): r.get("p95_latency_ms") for r in ue_rows},
        "p99_latency_ms": {(r["cell_id"], int(r["ue_index"]), r["direction"]): r.get("p99_latency_ms") for r in ue_rows},
        "prb_symbol_share": {(r["cell_id"], int(r["ue_index"]), r["direction"]): r.get("prb_symbol_share") for r in grant_rows},
    }
    for r in ue_rows:
        if int(r["ue_index"]) != 6:
            continue
        peer_cell_rows = [x for x in ue_rows if x["cell_id"] == r["cell_id"]
                          and x["direction"] == r["direction"] and int(x["ue_index"]) in range(1, 6)]
        for metric, values in metric_sources.items():
            target = values.get((r["cell_id"], 6, r["direction"]))
            peers = [values.get((x["cell_id"], int(x["ue_index"]), x["direction"])) for x in peer_cell_rows]
            peers = [float(x) for x in peers if x not in (None, "")]
            try:
                target = float(target) if target not in (None, "") else None
            except (TypeError, ValueError):
                target = None
            peer_mean = statistics.mean(peers) if peers else None
            if target is not None and peer_mean is not None:
                peer_seed_rows.append({**{k: r[k] for k in (*FACTORS, "seed", "direction", "cell_id")},
                                       "metric": metric, "ue6_value": target,
                                       "peer_ue1_to_ue5_mean": peer_mean,
                                       "ue6_minus_peer_mean": target - peer_mean,
                                       "ue6_received_latency_n": int(r["received_latency_n"]),
                                       "peer_min_received_latency_n": min(int(x["received_latency_n"]) for x in peer_cell_rows),
                                       "peer_ues_below_1000_latency_samples": sum(int(x["received_latency_n"]) < 1000 for x in peer_cell_rows),
                                       "p99_comparison_adequacy": (
                                           "adequate-by-1000-sample-rule"
                                           if metric == "p99_latency_ms" and int(r["received_latency_n"]) >= 1000
                                           and all(int(x["received_latency_n"]) >= 1000 for x in peer_cell_rows)
                                           else "inadequate-by-1000-sample-rule" if metric == "p99_latency_ms"
                                           else "not-applicable")})

    peer_groups = {}
    for r in peer_seed_rows:
        key = tuple(r[k] for k in (*FACTORS, "direction", "metric"))
        peer_groups.setdefault(key, []).append(r)
    peer_summary = []
    for key, rows in sorted(peer_groups.items(), key=lambda x: str(x[0])):
        differences = [float(r["ue6_minus_peer_mean"]) for r in rows]
        ue6_values = [float(r["ue6_value"]) for r in rows]
        peer_values = [float(r["peer_ue1_to_ue5_mean"]) for r in rows]
        mean, sd, low, high, n = mean_sd_ci(differences)
        peer_summary.append({**dict(zip((*FACTORS, "direction", "metric"), key)),
                             "paired_seed_n": n, "mean_ue6": statistics.mean(ue6_values),
                             "mean_peer_ue1_to_ue5": statistics.mean(peer_values),
                             "mean_ue6_minus_peer": mean, "sd_paired_difference": sd,
                             "ci95_low": low, "ci95_high": high,
                             "adequate_p99_seed_n": sum(r["p99_comparison_adequacy"] == "adequate-by-1000-sample-rule" for r in rows),
                             "inadequate_p99_seed_n": sum(r["p99_comparison_adequacy"] == "inadequate-by-1000-sample-rule" for r in rows)})

    # Paired MAC allocation contrasts use the same seed as the replicate unit.
    mac_contrast_rows = []
    mac_specs = [("channel", "ue6-nlos", "all-los"),
                 ("mobility", "controlled-linear", "stationary"),
                 ("load", "contending", "light"),
                 ("load", "dl-contending", "light"),
                 ("load", "ul-contending", "light"),
                 ("load", "dl-contending", "ul-contending"),
                 ("policy", "TopKCqi", "RoundRobin")]
    for factor, treated_value, reference_value in mac_specs:
        other = [x for x in FACTORS if x != factor]
        pairs = {}
        for r in grant_rows:
            key = tuple(r.get(k) for k in (*other, "seed", "direction", "ue_index"))
            if r.get(factor) == treated_value:
                pairs.setdefault(key, {})["treated"] = r
            if r.get(factor) == reference_value:
                pairs.setdefault(key, {})["reference"] = r
        for key, pair in pairs.items():
            if "treated" not in pair or "reference" not in pair:
                continue
            tr, ref = pair["treated"], pair["reference"]
            row = {**dict(zip(other, key[:len(other)])), "seed": key[len(other)],
                   "direction": key[len(other)+1], "ue_index": key[len(other)+2],
                   "factor": factor, "contrast": f"{treated_value} - {reference_value}"}
            for metric in ("prb_symbols", "prb_symbol_share", "grant_count", "mean_mcs"):
                a, b = tr.get(metric), ref.get(metric)
                row[f"{metric}_difference"] = (float(a) - float(b)
                                                 if a not in (None, "") and b not in (None, "") else None)
            mac_contrast_rows.append(row)

    mac_grouped = {}
    for r in mac_contrast_rows:
        group = (r["factor"], r["contrast"],
                 tuple(r.get(k) for k in FACTORS if k != r["factor"]),
                 r["direction"], int(r["ue_index"]))
        for metric in ("prb_symbols", "prb_symbol_share", "grant_count", "mean_mcs"):
            value = r.get(f"{metric}_difference")
            if value is not None:
                mac_grouped.setdefault((group, metric), []).append(float(value))
    mac_summary = []
    for (group, metric), values in mac_grouped.items():
        factor, contrast, other_values, direction, ue = group
        mean, sd, low, high, n = mean_sd_ci(values)
        mac_summary.append({"factor": factor, "contrast": contrast,
                            **dict(zip((x for x in FACTORS if x != factor), other_values)),
                            "direction": direction, "ue_index": ue, "metric": metric,
                            "paired_seed_n": n, "mean_paired_difference": mean,
                            "sd_paired_difference": sd, "ci95_low": low, "ci95_high": high})

    adequacy_groups = {}
    for r in ue_rows:
        key = tuple(r.get(k) for k in (*FACTORS, "direction", "ue_index"))
        counts = adequacy_groups.setdefault(key, {"runs": 0, "n_lt_1000": 0, "n_zero": 0})
        counts["runs"] += 1
        n = int(r["received_latency_n"])
        counts["n_lt_1000"] += n < 1000
        counts["n_zero"] += n == 0

    write_csv(OUT / "run-audit.csv", audit)
    write_csv(OUT / "per-run-ue-metrics.csv", ue_rows)
    write_csv(OUT / "per-run-ue-grants.csv", grant_rows)
    write_csv(OUT / "per-run-ue-demand.csv", demand_rows)
    write_csv(OUT / "channel-mobility-audit.csv", channel_audit)
    write_csv(OUT / "ue6-versus-peer-by-seed.csv", peer_seed_rows)
    write_csv(OUT / "ue6-versus-peer-summary.csv", peer_summary)
    write_csv(OUT / "paired-mac-resource-contrasts.csv", mac_contrast_rows)
    write_csv(OUT / "paired-mac-resource-summary.csv", mac_summary)
    write_csv(OUT / "p99-sample-adequacy.csv", [
        {**dict(zip((*FACTORS, "direction", "ue_index"), key)), **counts}
        for key, counts in sorted(adequacy_groups.items(), key=lambda x: str(x[0]))
    ])

    demand_lookup = {(r["cell_id"], r["seed"], r["ue_index"], r["direction"]): r for r in demand_rows}
    calibration_groups = {}
    for row in ue_rows:
        demand = demand_lookup.get((row["cell_id"], row["seed"], row["ue_index"], row["direction"]))
        if demand is None:
            continue
        key = (row["channel"], row["mobility"], row["load"], row["policy"], row["direction"])
        agg = calibration_groups.setdefault(key, {"mean_queue_bytes": [], "nonempty_fraction": [],
                                                    "tx_rate_bps": [], "rx_goodput_bps": []})
        agg["mean_queue_bytes"].append(demand["mean_queue_bytes"])
        agg["nonempty_fraction"].append(demand["fraction_nonempty_queue"])
        if row["application_tx_rate_bps"] is not None:
            agg["tx_rate_bps"].append(row["application_tx_rate_bps"])
        if row["rx_goodput_bps"] is not None:
            agg["rx_goodput_bps"].append(row["rx_goodput_bps"])
    calibration_rows = []
    for key, agg in sorted(calibration_groups.items()):
        base = dict(zip(("channel", "mobility", "load", "policy", "direction"), key))
        for metric, vals in agg.items():
            base[f"{metric}_mean"] = statistics.mean(vals) if vals else None
            base[f"{metric}_seed_ue_observations"] = len(vals)
        calibration_rows.append(base)
    write_csv(OUT / "load-calibration-summary.csv", calibration_rows)

    grouped = {}
    for row in ue_rows:
        key = tuple(row.get(k) for k in (*FACTORS, "direction", "ue_index"))
        grouped.setdefault(key, []).append(row)
    seed_summary = []
    for key, rows in sorted(grouped.items(), key=lambda x: str(x[0])):
        base = dict(zip((*FACTORS, "direction", "ue_index"), key))
        for metric in ("application_tx_rate_bps", "rx_goodput_bps", "pdr", "mean_latency_ms", "p50_latency_ms", "p95_latency_ms", "p99_latency_ms", "rx_unique_packets"):
            vals = [float(r[metric]) for r in rows if r.get(metric) is not None]
            m, sd, lo, hi, n = mean_sd_ci(vals)
            base.update({f"{metric}_mean": m, f"{metric}_sd": sd,
                         f"{metric}_ci95_low": lo, f"{metric}_ci95_high": hi,
                         f"{metric}_seed_n": n})
        seed_summary.append(base)
    write_csv(OUT / "seed-level-summary.csv", seed_summary)

    by_key = {tuple(r.get(k) for k in (*FACTORS, "seed", "direction", "ue_index")): r for r in ue_rows}
    contrasts = []
    contrast_specs = [("channel", "ue6-nlos", "all-los"),
                      ("mobility", "controlled-linear", "stationary"),
                      ("load", "contending", "light"),
                      ("load", "dl-contending", "light"),
                      ("load", "ul-contending", "light"),
                      ("load", "dl-contending", "ul-contending"),
                      ("policy", "TopKCqi", "RoundRobin")]
    for factor, treated, reference in contrast_specs:
        other = [x for x in FACTORS if x != factor]
        pairs_by = {}
        for r in ue_rows:
            if factor in r and r[factor] == treated:
                base = tuple(r.get(k) for k in (*other, "seed", "direction", "ue_index"))
                pairs_by.setdefault(base, {})["treated"] = r
            if factor in r and r[factor] == reference:
                base = tuple(r.get(k) for k in (*other, "seed", "direction", "ue_index"))
                pairs_by.setdefault(base, {})["reference"] = r
        metric_values = {}
        for base, pair in pairs_by.items():
            if "treated" not in pair or "reference" not in pair:
                continue
            tr, ref = pair["treated"], pair["reference"]
            row = {**dict(zip(other, base[:len(other)])), "seed": base[len(other)],
                   "direction": base[len(other)+1], "ue_index": base[len(other)+2],
                   "factor": factor, "contrast": f"{treated} - {reference}"}
            for metric in ("application_tx_rate_bps", "rx_goodput_bps", "pdr", "p95_latency_ms", "p99_latency_ms"):
                a, b = tr.get(metric), ref.get(metric)
                row[f"{metric}_difference"] = float(a) - float(b) if a is not None and b is not None else None
                if metric == "p99_latency_ms":
                    row["p99_samples_treated"] = int(tr["received_latency_n"])
                    row["p99_samples_reference"] = int(ref["received_latency_n"])
                    row["p99_pair_adequacy"] = (
                        "adequate-by-1000-sample-rule"
                        if int(tr["received_latency_n"]) >= 1000 and int(ref["received_latency_n"]) >= 1000
                        else "inadequate-by-1000-sample-rule")
                if row[f"{metric}_difference"] is not None:
                    metric_values.setdefault((tuple(row.get(k) for k in other), row["direction"],
                                              row["ue_index"], metric), []).append(row[f"{metric}_difference"])
            contrasts.append(row)
    write_csv(OUT / "paired-seed-contrasts.csv", contrasts)
    interaction_seed_rows, interaction_summary = build_policy_channel_interactions(ue_rows, grant_rows)
    write_csv(OUT / "policy-by-channel-interaction-by-seed.csv", interaction_seed_rows)
    write_csv(OUT / "policy-by-channel-interaction-summary.csv", interaction_summary)
    paired_groups = {}
    for row in contrasts:
        grouping = (row["factor"], row["contrast"],
                    tuple(row.get(k) for k in FACTORS if k != row["factor"]),
                    row["direction"], row["ue_index"])
        for metric in ("application_tx_rate_bps", "rx_goodput_bps", "pdr", "p95_latency_ms", "p99_latency_ms"):
            value = row.get(f"{metric}_difference")
            if value is not None:
                paired_groups.setdefault((grouping, metric), []).append(float(value))
    paired_summary = []
    for (grouping, metric), values in paired_groups.items():
        factor, contrast, other_values, direction, ue = grouping
        mean, sd, low, high, n = mean_sd_ci(values)
        p99_pairs = [r for r in contrasts if r["factor"] == factor and r["contrast"] == contrast
                     and tuple(r.get(k) for k in FACTORS if k != factor) == other_values
                     and r["direction"] == direction and int(r["ue_index"]) == ue
                     and r.get("p99_pair_adequacy")]
        paired_summary.append({
            "factor": factor, "contrast": contrast,
            **dict(zip((x for x in FACTORS if x != factor), other_values)),
            "direction": direction, "ue_index": ue, "metric": metric,
            "paired_seed_n": n, "mean_paired_difference": mean,
            "sd_paired_difference": sd, "ci95_low": low, "ci95_high": high,
            "adequate_p99_pair_n": sum(r.get("p99_pair_adequacy") == "adequate-by-1000-sample-rule" for r in p99_pairs),
            "inadequate_p99_pair_n": sum(r.get("p99_pair_adequacy") == "inadequate-by-1000-sample-rule" for r in p99_pairs),
        })
    write_csv(OUT / "paired-contrast-summary.csv", paired_summary)

    base_planned = json.loads((CAMPAIGN / "planned-matrix.json").read_text())
    extension_path = CAMPAIGN / "directional-load-extension.json"
    extension_cells = json.loads(extension_path.read_text())["cells"] if extension_path.exists() else []
    planned_total = len(unique_planned_cells(base_planned["cells"], extension_cells))
    counts = {"planned_cells": planned_total,
              "attempts": len(audit), "successful_attempts": sum(bool(x["successful"]) for x in audit),
              "failed_attempts": sum(not bool(x["successful"]) for x in audit),
              "measurement_complete_attempts": sum(bool(x["measurement_complete"]) for x in audit),
              "successful_but_measurement_incomplete_attempts": sum(bool(x["successful"]) and not bool(x["measurement_complete"]) for x in audit),
              "successful_cells": len(primary_attempt),
              "cells_missing_complete_measurement": planned_total - len(primary_attempt),
              "per_run_ue_rows": len(ue_rows), "per_run_grant_rows": len(grant_rows),
              "per_run_demand_rows": len(demand_rows), "load_calibration_rows": len(calibration_rows)}
    (OUT / "campaign-counts.json").write_text(json.dumps(counts, indent=2) + "\n")
    print(json.dumps(counts, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        (OUT / "figures").mkdir(parents=True, exist_ok=True)
        for metric, ylabel, filename in (("p95_latency_ms", "P95 application delay (ms)", "p95-latency.png"),
                                         ("p99_latency_ms", "P99 application delay (ms)", "p99-latency.png"),
                                         ("rx_goodput_bps", "Received goodput (bit/s)", "rx-goodput.png")):
            fig, ax = plt.subplots(figsize=(9, 5.4), constrained_layout=True)
            labels, values = [], []
            for channel in ("all-los", "ue6-nlos"):
                for load in ("light", "contending", "dl-contending", "ul-contending"):
                    vals = [float(r[metric]) for r in ue_rows if r.get(metric) is not None
                            and r["channel"] == channel and r["load"] == load
                            and r["ue_index"] == 6 and r["direction"] == "DL"
                            and (metric != "p99_latency_ms" or
                                 r["p99_sample_adequacy"] == "at-least-1000-received")]
                    if vals:
                        labels.append(f"{channel}\n{load}")
                        values.append(vals)
            if values:
                ax.boxplot(values, tick_labels=labels, showfliers=False)
                ax.set_ylabel(ylabel)
                ax.set_title("UE6 DL outcome by channel and offered-load regime (run-level values)")
                ax.grid(axis="y", alpha=.25)
                fig.savefig(OUT / "figures" / filename, dpi=300)
            plt.close(fig)

        grant_totals = {}
        for row in grant_rows:
            if row["load"] != "contending" or row["direction"] != "DL":
                continue
            key = row["cell_id"]
            grant_totals.setdefault(key, {"meta": row, "ues": {}})["ues"][row["ue_index"]] = row["prb_symbols"]
        shares = {}
        for run in grant_totals.values():
            ue_values = run["ues"]
            total = sum(ue_values.values())
            if not total:
                continue
            meta = run["meta"]
            for ue in range(1, 7):
                group = (meta["channel"], meta["policy"], ue)
                shares.setdefault(group, []).append(100 * ue_values.get(ue, 0) / total)
        fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
        colors = {"all-los": "#2878B5", "ue6-nlos": "#D95319"}
        patterns = [("all-los", "RoundRobin"), ("all-los", "TopKCqi"),
                    ("ue6-nlos", "RoundRobin"), ("ue6-nlos", "TopKCqi")]
        width = .19
        xs = list(range(1, 7))
        for idx, (channel, policy) in enumerate(patterns):
            series = [shares.get((channel, policy, ue), [0]) for ue in xs]
            vals = [statistics.mean(v) for v in series]
            errs = [statistics.stdev(v) if len(v) > 1 else 0 for v in series]
            offset = (idx - 1.5) * width
            ax.bar([x + offset for x in xs], vals, yerr=errs, capsize=2, width=width,
                   color=colors[channel], alpha=.65 if policy == "RoundRobin" else 1.0,
                   label=f"{channel}, {policy}")
        ax.set_xticks(xs, [f"UE{u}" for u in xs])
        ax.set_ylabel("Share of applied downlink PRB-symbol grants (%)")
        ax.set_title("Downlink resource redistribution under contending offered load")
        ax.grid(axis="y", alpha=.25)
        ax.legend(frameon=False, ncol=2)
        fig.savefig(OUT / "figures" / "dl-resource-redistribution.png", dpi=300)
        plt.close(fig)

        # All-UE P95 outcomes for a fixed stationary, contending load block.
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True, constrained_layout=True)
        line_specs = [("all-los", "RoundRobin", "#2878B5", "-") ,
                      ("all-los", "TopKCqi", "#2878B5", "--"),
                      ("ue6-nlos", "RoundRobin", "#D95319", "-"),
                      ("ue6-nlos", "TopKCqi", "#D95319", "--")]
        for ax, direction in zip(axes, ("DL", "UL")):
            for channel, policy, color, style in line_specs:
                means, lows, highs = [], [], []
                for ue in range(1, 7):
                    values = [float(row["p95_latency_ms"]) for row in ue_rows
                              if row["mobility"] == "stationary" and row["load"] == "contending"
                              and row["channel"] == channel and row["policy"] == policy
                              and row["direction"] == direction and int(row["ue_index"]) == ue
                              and row["p95_latency_ms"] is not None]
                    mean, _, low, high, n = mean_sd_ci(values)
                    means.append(mean if mean is not None else float("nan"))
                    lows.append(mean-low if n > 1 and low is not None else 0)
                    highs.append(high-mean if n > 1 and high is not None else 0)
                    if mean is not None:
                        ax.annotate(f"n={n}", (ue, mean), xytext=(2, 4), textcoords="offset points",
                                    fontsize=6, color=color)
                ax.errorbar(range(1, 7), means, yerr=[lows, highs], marker="o", capsize=2,
                            color=color, linestyle=style, label=f"{channel}, {policy}")
            ax.set_title(f"{direction}; stationary, contending")
            ax.set_xlabel("UE index")
            ax.set_xticks(range(1, 7))
            ax.grid(alpha=.25)
        axes[0].set_yscale("log")
        axes[0].set_ylabel("P95 received application delay (ms; log scale)")
        axes[1].legend(frameon=False, fontsize=8)
        fig.savefig(OUT / "figures" / "per-ue-p95-channel-policy.png", dpi=300)
        plt.close(fig)

        # Channel difference-in-differences of the matched TopKCqi-RoundRobin P95 effect.
        interaction_path = OUT / "policy-by-channel-interaction-summary.csv"
        interaction_rows = read_csv(interaction_path)
        fig, axes = plt.subplots(2, 4, figsize=(15, 7), sharey="row", constrained_layout=True)
        for row_index, direction in enumerate(("DL", "UL")):
            for col_index, load in enumerate(("light", "contending", "dl-contending", "ul-contending")):
                ax = axes[row_index][col_index]
                selected = [row for row in interaction_rows
                            if row["mobility"] == "stationary" and row["load"] == load
                            and row["direction"] == direction and row["metric"] == "p95_latency_ms"]
                selected.sort(key=lambda row: int(row["ue_index"]))
                xs = [int(row["ue_index"]) for row in selected]
                ys = [float(row["mean_policy_effect_difference_in_differences"]) for row in selected]
                low = [y-float(row["ci95_low"]) for y, row in zip(ys, selected)]
                high = [float(row["ci95_high"])-y for y, row in zip(ys, selected)]
                ax.axhline(0, color="black", linewidth=.8)
                ax.errorbar(xs, ys, yerr=[low, high], fmt="o", capsize=2, color="#5B4B8A")
                for x, y, row in zip(xs, ys, selected):
                    ax.annotate(f"n={row['paired_seed_n']}", (x, y), xytext=(2, 4),
                                textcoords="offset points", fontsize=6)
                ax.set_title(f"{direction}: {load}")
                ax.set_xticks(range(1, 7))
                ax.grid(alpha=.25)
        axes[0][0].set_ylabel("NLOS policy effect − LOS policy effect\nP95 delay (ms)")
        axes[1][0].set_ylabel("NLOS policy effect − LOS policy effect\nP95 delay (ms)")
        fig.savefig(OUT / "figures" / "policy-channel-p95-interaction.png", dpi=300)
        plt.close(fig)

        # Trace CQI and MCS for the predetermined first-seed NLOS contention pilot cell.
        representative_id = "ue6-nlos-stationary-contending-topkcqi-seed11"
        representative = next((path for path in primary_attempt.values()
                               if path.parent.name == representative_id), None)
        if representative is not None:
            rnti_to_ue = {}
            for event in read_csv(representative / "logs/packet-events.csv"):
                if event.get("rnti"):
                    rnti_to_ue[int(event["rnti"])] = int(event["ue_index"])
            cqi_bins, mcs_bins = {}, {}
            for trace in read_csv(representative / "logs/mac-demand.csv"):
                if trace.get("direction") == "0" and int(trace["rnti"]) in rnti_to_ue:
                    ue = rnti_to_ue[int(trace["rnti"])]
                    second = int(trace["time_ns"]) // 1_000_000_000
                    cqi_bins.setdefault((ue, second), []).append(int(trace["cqi"]))
            for trace in read_csv(representative / "logs/mac-grants.csv"):
                if trace.get("direction") == "DL" and int(trace["rnti"]) in rnti_to_ue:
                    ue = rnti_to_ue[int(trace["rnti"])]
                    second = int(trace["time_ns"]) // 1_000_000_000
                    mcs_bins.setdefault((ue, second), []).append(int(trace["mcs"]))
            cqi_series, mcs_series = ({ue: ([], []) for ue in range(1, 7)},
                                      {ue: ([], []) for ue in range(1, 7)})
            for (ue, second), values in sorted(cqi_bins.items()):
                cqi_series[ue][0].append(second + .5)
                cqi_series[ue][1].append(statistics.median(values))
            for (ue, second), values in sorted(mcs_bins.items()):
                mcs_series[ue][0].append(second + .5)
                mcs_series[ue][1].append(statistics.mean(values))
            fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
            for ue in range(1, 7):
                axes[0].plot(*cqi_series[ue], marker="o", markersize=3, linewidth=1, label=f"UE{ue}")
                axes[1].plot(*mcs_series[ue], marker="o", markersize=3, linewidth=1, label=f"UE{ue}")
            axes[0].set_ylabel("Median observed DL CQI / 1 s")
            axes[1].set_ylabel("Mean observed DL grant MCS / 1 s")
            axes[1].set_xlabel("Simulation time (s)")
            axes[0].set_title(f"Observed CQI/MCS trace; {representative_id}")
            axes[0].legend(frameon=False, ncol=6, fontsize=8)
            for ax in axes:
                ax.grid(alpha=.2)
            fig.savefig(OUT / "figures" / "representative-cqi-mcs-trace.png", dpi=300)
            plt.close(fig)
    except ImportError:
        (OUT / "PLOT-LIMITATION.txt").write_text("matplotlib unavailable; CSV data are complete, plots not generated.\n")
    result_hashes = sorted(p for p in OUT.rglob("*")
                           if p.is_file() and p.name != "results-sha256.txt")
    (OUT / "results-sha256.txt").write_text("".join(
        f"{sha256(path)}  {path.relative_to(ROOT)}\n" for path in result_hashes
    ))


if __name__ == "__main__":
    main()
