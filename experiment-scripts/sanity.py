#!/usr/bin/env python3
"""Build, test, run a bounded G1 sanity matrix, and report every core KPI.

Must run on the provisioned WSL2 environment. Never edits the full campaign's
raw results. See AGENTS.md and the campaign README for scientific limitations.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT
SIM = ROOT / "simulator/ns-3.48"
IBORAN = SIM / "contrib/iboran"
OVERRIDES = ROOT / "simulator/overrides/iboran"
SPEC = json.loads((ROOT / "configs/experiment.json").read_text())
RUN_SCRIPT = ROOT / "experiment-scripts/run_campaign.py"
ANALYZE_SCRIPT = ROOT / "experiment-scripts/analyze_campaign.py"
STARVATION_SECONDS = 1.0  # Diagnostic threshold, not a 3GPP requirement.
MAX_TRACE_GAP_NS = 100_000_000  # Break backlog streaks when reports are absent.


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def source_manifest() -> list[tuple[str, Path, Path]]:
    entries = []
    for raw_line in (OVERRIDES / "SHA256SUMS").read_text().splitlines():
        if not raw_line.strip():
            continue
        expected, relative = raw_line.split(maxsplit=1)
        source = (OVERRIDES / relative).resolve()
        destination = (IBORAN / relative).resolve()
        if not source.is_relative_to(OVERRIDES.resolve()) or not destination.is_relative_to(IBORAN.resolve()):
            raise ValueError(f"unsafe override path: {relative}")
        if not source.is_file() or digest(source) != expected:
            raise RuntimeError(f"source override checksum mismatch: {source}")
        entries.append((relative, source, destination))
    return entries


def reconcile_sources(backup: Path, apply: bool) -> None:
    changes = [(name, source, target) for name, source, target in source_manifest()
               if not target.is_file() or digest(source) != digest(target)]
    if not changes:
        print("SOURCE CHECK: all pinned campaign overrides match local simulator", flush=True)
        return
    print("SOURCE CHECK: local simulator differs from committed package:", flush=True)
    for name, _, _ in changes:
        print(f"  {name}", flush=True)
    if not apply:
        raise RuntimeError("Refusing to use mismatched source. Review differences and rerun with --apply-overrides.")
    backup.mkdir(parents=True, exist_ok=False)
    for name, source, target in changes:
        if target.is_file():
            old = backup / name
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, old)
        else:
            raise RuntimeError(f"missing upstream file, cannot safely overwrite: {target}")
    for name, source, target in changes:
        shutil.copy2(source, target)
    print(f"Applied reviewed overrides; original files backed up to {backup}", flush=True)


def run_step(label: str, command: list[str], cwd: Path) -> None:
    print(f"\n=== {label} ===\n$ {' '.join(map(str, command))}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise RuntimeError(f"required sanity result missing: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def fnum(value, default=0.0):
    if value in ("", None, "None"):
        return default
    return float(value)


def jain(values: list[float]):
    if not values:
        return None
    denom = len(values) * sum(x * x for x in values)
    return sum(values) ** 2 / denom if denom > 0 else None


def longest_backlogged_grant_gap(demand_samples: list[tuple[int, int]],
                                  grant_times: list[int]) -> float:
    """Largest time without an actual MAC grant while buffer is observed nonempty.

    A zero backlog or a long missing-report interval resets the streak. Gaps
    are measured only within observed backlog, not during idle traffic.
    """
    points = sorted(demand_samples)
    grants = sorted(grant_times)
    start = last_sample = latest_service = None
    max_gap = 0
    for t, queue_bytes in points:
        if queue_bytes <= 0:
            start = last_sample = latest_service = None
            continue
        if last_sample is None or t - last_sample > MAX_TRACE_GAP_NS:
            start = latest_service = t
        ix = bisect_right(grants, t) - 1
        if ix >= 0 and grants[ix] >= start and grants[ix] > latest_service:
            latest_service = grants[ix]
        max_gap = max(max_gap, t - latest_service)
        last_sample = t
    return max_gap / 1_000_000_000


def pretty(value, digits=2) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


def summarize(campaign: Path, out: Path, expected_cells=20) -> dict:
    """Compute high-throughput KPIs plus grant starvation from raw MAC traces."""
    metrics = csv_rows(out / "per-run-ue-metrics.csv")
    grants = csv_rows(out / "per-run-ue-grants.csv")
    demand = csv_rows(out / "per-run-ue-demand.csv")
    audits = csv_rows(out / "run-audit.csv")
    channel = csv_rows(out / "channel-mobility-audit.csv")

    selected = [r for r in audits if r["selected_for_analysis"].lower() == "true"]
    selected_cells = {r["cell_id"] for r in selected}
    issues = []
    if len(selected_cells) != expected_cells:
        issues.append(f"Only {len(selected_cells)}/{expected_cells} valid run cells")
    if len(metrics) != expected_cells * 12:
        issues.append(f"Per-UE UL/DL results incomplete: {len(metrics)}/{expected_cells * 12}")
    for r in channel:
        if r.get("channel_position_audit_pass", "").lower() != "true":
            issues.append(f"Channel/mobility audit failed for {r['cell_id']}")

    grant_by_ue = {(r["cell_id"], r["direction"], str(r["ue_index"])): r for r in grants}
    demand_by_ue = {(r["cell_id"], r["direction"], str(r["ue_index"])): r for r in demand}
    metrics_by_case = {}
    enriched = []
    target_pdr = SPEC.get("experiment_intent", {}).get("reliability_target_pdr_exploratory")
    for r in metrics:
        case = (r["cell_id"], r["direction"])
        metrics_by_case.setdefault(case, []).append(r)
        ue = str(r["ue_index"])
        g = grant_by_ue.get((r["cell_id"], r["direction"], ue), {})
        d = demand_by_ue.get((r["cell_id"], r["direction"], ue), {})
        if not g or not d:
            issues.append(f"Missing MAC grant or demand measurement: {r['cell_id']} {r['direction']} UE{ue}")
        out_row = {
            **{key: r.get(key) for key in
               ("cell_id", "channel", "mobility", "load", "policy", "seed", "direction", "ue_index")},
            "offered_mbps": fnum(r.get("offered_bps_configured"), None) / 1e6
                            if r.get("offered_bps_configured") not in (None, "") else None,
            "application_tx_mbps": fnum(r.get("application_tx_rate_bps")) / 1e6,
            "rx_goodput_mbps": fnum(r.get("rx_goodput_bps")) / 1e6,
            "mac_actual_throughput_mbps": fnum(d.get("mean_actual_throughput_mbps"), None),
            "mac_achievable_rate_mbps": fnum(d.get("mean_achievable_rate_mbps"), None),
            "tx_packets": int(r.get("tx_packets") or 0),
            "rx_packets": int(r.get("rx_unique_packets") or 0),
            "pdr": fnum(r.get("pdr"), None),
            "observed_pdr_target": target_pdr,
            "observed_pdr_meets_target": (
                fnum(r.get("pdr"), None) >= target_pdr
                if r.get("pdr") not in ("", None) and target_pdr is not None
                else None
            ),
            "target_reliability_confidence_demonstrated": False,
            "application_latency_deadline_ms": SPEC.get("experiment_intent", {}).get("application_latency_deadline_ms"),
            "lost_or_unreceived": int(r.get("lost_or_unreceived_at_stop") or 0),
            "p50_ms": fnum(r.get("p50_latency_ms"), None),
            "p95_ms": fnum(r.get("p95_latency_ms"), None),
            "p99_ms": fnum(r.get("p99_latency_ms"), None),
            "received_latency_n": int(r.get("received_latency_n") or 0),
            "p99_sample_adequacy": r.get("p99_sample_adequacy"),
            "grant_count": int(g.get("grant_count") or 0),
            "prb_symbols": int(g.get("prb_symbols") or 0),
            "prb_symbol_share": fnum(g.get("prb_symbol_share"), None),
            "mean_mcs": fnum(g.get("mean_mcs"), None),
            "queue_nonempty_fraction": fnum(d.get("fraction_nonempty_queue"), None),
            "mean_queue_bytes": fnum(d.get("mean_queue_bytes"), None),
            "max_queue_bytes": fnum(d.get("max_queue_bytes"), None),
            "mean_cqi": fnum(d.get("mean_reported_cqi"), None),
            "duplicate_rx_packets": int(r.get("duplicate_rx_packets") or 0),
            "reordered_rx_events": int(r.get("reordered_rx_events") or 0),
        }
        if out_row["rx_packets"] > out_row["tx_packets"]:
            issues.append(f"Received count greater than transmitted: {r['cell_id']} {r['direction']} UE{ue}")
        if out_row["tx_packets"] == 0:
            issues.append(f"No application TX: {r['cell_id']} {r['direction']} UE{ue}")
        enriched.append(out_row)

    write_rows(out / "sanity-per-ue.csv", enriched)

    case_rows = []
    for (cid, direction), rows in sorted(metrics_by_case.items()):
        sample = rows[0]
        delivered = [fnum(r.get("rx_goodput_bps")) / 1e6 for r in rows]
        tx = [fnum(r.get("application_tx_rate_bps")) / 1e6 for r in rows]
        offered = [fnum(r.get("offered_bps_configured")) / 1e6 for r in rows]
        aggregated = {
            "cell_id": cid, "channel": sample["channel"], "mobility": sample["mobility"],
            "load": sample["load"], "policy": sample["policy"], "seed": sample["seed"],
            "direction": direction, "ue_count": len(rows),
            "configured_offered_mbps": sum(offered),
            "actual_application_tx_mbps": sum(tx),
            "received_goodput_mbps": sum(delivered),
            "goodput_over_actual_tx": sum(delivered) / sum(tx) if sum(tx) > 0 else None,
            "jain_goodput": jain(delivered),
            "jain_mac_prb_symbols": jain([
                fnum(grant_by_ue.get((cid, direction, str(x["ue_index"])), {}).get("prb_symbols"))
                for x in rows
            ]),
            "tx_packets": sum(int(r.get("tx_packets") or 0) for r in rows),
            "rx_packets": sum(int(r.get("rx_unique_packets") or 0) for r in rows),
            "ue_with_zero_goodput": sum(x <= 0 for x in delivered),
            "ue_with_inadequate_p99": sum(int(r.get("received_latency_n") or 0) < 1000 for r in rows),
        }
        case_rows.append(aggregated)
        if len(rows) != 6:
            issues.append(f"Expected 6 UE measurements in {cid} {direction}, found {len(rows)}")
    write_rows(out / "sanity-throughput-by-scenario.csv", case_rows)

    backlog_audit = []
    by_cell = {r["cell_id"]: r for r in selected}
    for cell_id, audit in sorted(by_cell.items()):
        rel = Path(audit["attempt"])
        attempt = ROOT / rel
        if not attempt.is_dir():
            issues.append(f"Selected attempt not accessible: {rel}")
            continue
        events = csv_rows(attempt / "logs/packet-events.csv")
        grant_rows = csv_rows(attempt / "logs/mac-grants.csv")
        demand_rows = csv_rows(attempt / "logs/mac-demand.csv")
        rnti_ue = {}
        for e in events:
            rnti = int(e.get("rnti") or 0)
            ue = int(e.get("ue_index") or 0)
            if rnti > 0 and ue > 0:
                rnti_ue.setdefault(rnti, set()).add(ue)
        for rnti, ues in rnti_ue.items():
            if len(ues) != 1:
                issues.append(f"Ambiguous RNTI to UE mapping in {cell_id}: {rnti} => {sorted(ues)}")
        actual = {}
        for grant in grant_rows:
            direction = str(grant["direction"]).upper()
            if direction not in ("DL", "UL"):
                continue
            key = (int(grant["rnti"]), direction)
            actual.setdefault(key, []).append(int(grant["time_ns"]))
        samples = {}
        for row in demand_rows:
            direction = "DL" if str(row["direction"]) == "0" else "UL" if str(row["direction"]) == "1" else str(row["direction"]).upper()
            if direction not in ("DL", "UL"):
                continue
            key = (int(row["rnti"]), direction)
            samples.setdefault(key, []).append((int(row["time_ns"]), int(row["buffer_bytes"])))
        for (rnti, direction), points in sorted(samples.items()):
            grant_times = sorted(actual.get((rnti, direction), []))
            max_gap = longest_backlogged_grant_gap(points, grant_times)
            backlogged = [t for t, amount in points if amount > 0]
            first_grant = min(grant_times) / 1e9 if grant_times else None
            ue = next(iter(rnti_ue[rnti])) if rnti in rnti_ue and len(rnti_ue[rnti]) == 1 else None
            bad = max_gap >= STARVATION_SECONDS
            backlog_audit.append({
                "cell_id": cell_id, "channel": audit["channel"], "mobility": audit["mobility"],
                "load": audit["load"], "policy": audit["policy"], "seed": audit["seed"],
                "direction": direction, "rnti": rnti, "ue_index": ue,
                "demand_samples": len(points), "backlogged_samples": len(backlogged),
                "applied_grant_count": len(grant_times), "first_grant_s": first_grant,
                "max_backlogged_without_grant_s": round(max_gap, 6),
                "starvation_diagnostic": bad,
            })
            if bad and audit["policy"] == "RoundRobin":
                issues.append(f"RoundRobin service starvation {cell_id} {direction} RNTI {rnti}: {max_gap:.3f}s")
        if not (attempt / "logs/mac-cqi-input-state.csv").is_file():
            issues.append(f"Missing CQI input-state trace: {cell_id}")
    write_rows(out / "sanity-starvation.csv", backlog_audit)

    observed_topk = [r for r in backlog_audit
                     if r["policy"] == "TopKCqi" and r["starvation_diagnostic"]]
    problematic_rr = [r for r in backlog_audit
                      if r["policy"] == "RoundRobin" and r["starvation_diagnostic"]]
    # These are one-seed engineering diagnostics, not statistical significance.
    measured_pdr_met = sum(
        x["observed_pdr_meets_target"] is True for x in enriched
    )
    measured_pdr_failed = sum(
        x["observed_pdr_meets_target"] is False for x in enriched
    )
    verdict = {
        "status": "PASS" if not issues else "FAIL",
        "study_objective": SPEC.get("experiment_intent", {}).get("mode"),
        "observed_pdr_goal": target_pdr,
        "per_ue_direction_observed_pdr_target_met": measured_pdr_met,
        "per_ue_direction_observed_pdr_target_not_met": measured_pdr_failed,
        "ultra_reliable_service_claim": "NOT_ESTABLISHED: diagnostic observations only; needs PDR confidence bounds, deadline and replicated tests",
        "completed_valid_cells": len(selected_cells),
        "expected_cells": expected_cells,
        "analyzed_per_ue_direction_rows": len(enriched),
        "throughput_scenario_direction_rows": len(case_rows),
        "round_robin_backlogged_grant_gap_flags": len(problematic_rr),
        "topkcqi_backlogged_grant_gap_flags": len(observed_topk),
        "threshold_seconds": STARVATION_SECONDS,
        "issues": issues,
        "scientific_scope": "single-seed engineering sanity only; not publication inference",
    }
    (out / "sanity-verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")

    high = [r for r in case_rows if r["load"] != "light"]
    md = [
        "# G1 scheduler / high-throughput sanity report",
        "",
        f"**Verdict:** {verdict['status']} — {len(selected_cells)}/{expected_cells} valid cells, "
        f"{len(problematic_rr)} RoundRobin starvation flags, {len(observed_topk)} TopKCqi starvation flags.",
        "",
        "This is a one-seed diagnostic, **not** evidence for statistical or publication claims. "
        f"Exploratory PDR target {target_pdr}; observed UE/direction cells meeting it: {measured_pdr_met}, "
        f"below target: {measured_pdr_failed}. No ultra-reliable service compliance claim is established. "
        "The 1-second continuous-backlog grant-gap threshold is an engineering alarm, not a standard.",
        "",
        "## High-throughput DL/UL results",
        "",
        "Configured offered Mbps is the sum over six UEs. Actual TX is application traffic; "
        "goodput is received application payload throughput. MAC-reported actual throughput, "
        "per-UE CQI, MCS, and queue demand are in `sanity-per-ue.csv`.",
        "",
        "| Channel | Motion | Load | Policy | Dir | Offered Mbps | TX Mbps | Goodput Mbps | Jain goodput | Zero-goodput UEs |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in high:
        md.append(
            f"| {r['channel']} | {r['mobility']} | {r['load']} | {r['policy']} | {r['direction']} "
            f"| {pretty(r['configured_offered_mbps'])} | {pretty(r['actual_application_tx_mbps'])} "
            f"| {pretty(r['received_goodput_mbps'])} | {pretty(r['jain_goodput'], 3)} "
            f"| {r['ue_with_zero_goodput']} |"
        )
    md.extend([
        "",
        "## Additional measured dimensions",
        "",
        "Per-UE CSV: UL/DL offered, application TX, RX goodput, MAC actual throughput, "
        "MAC achievable rate, PDR/loss, P50/P95/P99 latency, sample sizes/censoring, "
        "duplicate/reordered packets, actual grants and PRB-symbol shares, MCS, CQI, and queue occupancy.",
        "",
        "Starvation CSV: per-RNTI first actual grant, backlog observations, and maximum "
        "grantless interval while demand is continuously observed. "
        "TopKCqi `k=1` may legitimately starve lower-CQI UEs; do not treat it as a fairness policy.",
        "",
        "The analyzer also outputs paired LOS/NLOS contrasts and channel/mobility diagnostics. "
        "P99 from fewer than 1,000 received packets is flagged exploratory, not zero.",
        "",
        "## Diagnostic failures",
        "",
    ])
    md.extend([f"- {issue}" for issue in issues] if issues else ["No sanity-gate violations detected."])
    md.extend([
        "",
        "## Files",
        "",
        "- `sanity-throughput-by-scenario.csv`: scenario/direction throughput and fairness",
        "- `sanity-per-ue.csv`: all engineering metrics per UE and direction",
        "- `sanity-starvation.csv`: raw demand/grant starvation diagnostics",
        "- `per-run-ue-metrics.csv`, `per-run-ue-grants.csv`, `per-run-ue-demand.csv`: canonical analyzer output",
        "- `paired-seed-contrasts.csv`, `paired-mac-resource-contrasts.csv`: exploratory single-seed comparisons",
        "- `channel-mobility-audit.csv`, `run-audit.csv`: experimental validity",
        "- `sanity-verdict.json`: machine-readable diagnostics",
        "",
    ])
    (out / "sanity-summary.md").write_text("\n".join(md))
    print(f"\n=== HIGH-THROUGHPUT SANITY ===", flush=True)
    for r in high:
        if r["mobility"] == "stationary":
            print(f"{r['channel']:8} {r['load']:14} {r['policy']:10} {r['direction']}: "
                  f"offered={r['configured_offered_mbps']:.2f}, TX={r['actual_application_tx_mbps']:.2f}, "
                  f"RX goodput={r['received_goodput_mbps']:.2f} Mbps; "
                  f"Jain={pretty(r['jain_goodput'], 3)}", flush=True)
    print(f"VERDICT={verdict['status']}; RR starved={len(problematic_rr)}, "
          f"TopKCqi starved={len(observed_topk)}; report={out / 'sanity-summary.md'}", flush=True)
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-overrides", action="store_true",
                        help="After reviewing source differences, back up and sync committed source overrides")
    parser.add_argument("--jobs", type=int, default=2, help="Parallel ns-3 build jobs")
    parser.add_argument("--skip-build", action="store_true",
                        help="Only for reuse of already-verified simulator build")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if not (SIM / "ns3").exists() or not (SIM / ".venv/bin/python").exists():
        parser.error("Pinned ns-3 checkout or Python venv missing; follow bootstrap first")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{os.getpid()}"
    campaign = ROOT / "simulator/runs" / (SPEC["campaign_id"] + "-sanity") / stamp
    results = ROOT / "results" / (SPEC["campaign_id"] + "-sanity") / stamp
    campaign.mkdir(parents=True, exist_ok=False)
    print(f"Sanity raw output: {campaign}", flush=True)
    print(f"Sanity analysis output: {results}", flush=True)

    # Stop before building if source and the pinned local checkout disagree.
    reconcile_sources(campaign / "source-backups", apply=args.apply_overrides)
    run_step("Python scheduler regressions",
             [sys.executable, "-m", "unittest", "discover",
              "-s", str(ROOT / "tests"), "-v"], ROOT)
    if not args.skip_build:
        run_step("Build required NR simulation target",
                 ["./ns3", "build", "ns3iboran_nr", "-j", str(args.jobs)], SIM)
    run_step("Run bounded, 20-cell sanity matrix with tqdm",
             [sys.executable, str(RUN_SCRIPT), "--sanity-block",
              "--python", str(SIM / ".venv/bin/python"),
              "--campaign-root", str(campaign)], ROOT)
    run_step("Analyze all per-UE metrics and paired scenarios",
             [sys.executable, str(ANALYZE_SCRIPT), "--campaign-root", str(campaign),
              "--output-dir", str(results)], ROOT)
    verdict = summarize(campaign, results)
    return 0 if verdict["status"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FAILED: command exited {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode or 1)
