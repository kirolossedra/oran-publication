#!/usr/bin/env python3
"""Run and instrument a fixed TopKCqi arm paired with the RA-ENG-005 baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml


ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "simulator/ns-3.48"
IBORAN = SIM / "contrib/iboran"
CAMPAIGN = IBORAN / "model/iboran_campaign"
BASELINE_CONFIG = ROOT / "configs/scenarios/g1-loadcal-dl-contending.yaml"
POLICY_CONFIG = ROOT / "configs/scenarios/g1-stockpolicy-topkcqi.yaml"
BASELINE_RUN = ROOT / "simulator/logs/RA-ENG-005-20261112/calibration-run-003/dl-contending"

SOURCE_PATHS = (
    "model/iboran_campaign/iboran_orchestrator.py",
    "model/iboran_controller/iboran_dapp_mac_scheduler.py",
    "model/iboran_controller/iboran_xapp_mac_scheduler.py",
    "model/iboran_controller/iboran_dapp_algos/dapp_algos_factory.py",
    "model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection.py",
    "model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_round_robin.py",
    "model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_top_k.py",
    "model/iboran_controller/iboran_xapp_algos/xapp_algos_factory.py",
    "model/iboran_controller/iboran_xapp_algos/xapp_algo_rbg_bounding_bypass.py",
    "model/iboran_controller/iboran_xapp_algos/xapp_algo_rbg_bounding_clamp.py",
    "model/iboran_mac_scheduler/iboran-nr-mac-scheduler.cc",
    "model/iboran_ran_environment/iboran-nr-environment.cc",
    "model/iboran_interfaces/iboran-shm-structure.h",
    "model/iboran_interfaces/iboran_e2sm_dapp_structure.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_configs() -> tuple[dict, dict]:
    baseline = yaml.safe_load(BASELINE_CONFIG.read_text())
    candidate = yaml.safe_load(POLICY_CONFIG.read_text())
    expected = yaml.safe_load(BASELINE_RUN.joinpath("effective-run-config.yaml").read_text())
    for name, config in (("baseline", baseline), ("candidate", candidate), ("recorded baseline", expected)):
        common = config["common"]
        if common["ueNum"] != 6 or common["rngRun"] != 11:
            raise ValueError(f"{name}: expected six UEs and matched seed 11")
        if common["mobilityMode"] != "Fixed" or config["nr"]["channelCondition"] != "LOS":
            raise ValueError(f"{name}: topology/channel differs from the approved whole-cell LOS baseline")
        if common["trafficMode"] != "Udp" or common["ueNum"] != len(common["ueTraffic"]):
            raise ValueError(f"{name}: expected explicit per-UE UDP traffic")
        if name in ("baseline", "candidate"):
            if config["orchestrator"]["xapp_algo_rbg_bounding"] != "Bypass":
                raise ValueError(f"{name}: xApp must remain Bypass in the dApp-only comparison")
            if config["orchestrator"]["k"] != 1:
                raise ValueError(f"{name}: expected the paired k=1 load-calibration control")
        for ue, flow in enumerate(common["ueTraffic"]):
            if int(flow["ueIndex"]) != ue or (flow["startTime"], flow["stopTime"], flow["sinkStopTime"]) != (1.0, 8.0, 9.0):
                raise ValueError(f"{name}: UE identity or source/drain window differs at UE {ue}")
            expected_rate = 20_000 if ue == 0 else 6_000_000
            if flow["dlBitRate"] != expected_rate or flow["ulBitRate"] != 20_000:
                raise ValueError(f"{name}: expected the calibrated DL-only contention arm at UE {ue}")
    if baseline["orchestrator"]["dapp_algo_ue_selection"] != "RoundRobin":
        raise ValueError("baseline config is not the RA-ENG-005 RoundRobin arm")
    if candidate["orchestrator"]["dapp_algo_ue_selection"] != "TopKCqi":
        raise ValueError("candidate must be the stock TopKCqi arm")
    if expected["orchestrator"]["dapp_algo_ue_selection"] != "RoundRobin":
        raise ValueError("recorded RA-ENG-005 run is not the RoundRobin reference")

    base_comparable = json.loads(json.dumps(baseline))
    cand_comparable = json.loads(json.dumps(candidate))
    base_comparable["orchestrator"].pop("dapp_algo_ue_selection")
    cand_comparable["orchestrator"].pop("dapp_algo_ue_selection")
    expected_comparable = json.loads(json.dumps(expected))
    expected_comparable.pop("campaignId", None)
    expected_comparable.pop("outputDir", None)
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
    # Effective runner fields are allowed; compare all explicitly configured keys.
    def subset_matches(config: dict, reference: dict) -> bool:
        if isinstance(reference, dict):
            return isinstance(config, dict) and all(
                key in config and subset_matches(config[key], value)
                for key, value in reference.items()
            )
        if isinstance(reference, list):
            return isinstance(config, list) and len(config) == len(reference) and all(
                subset_matches(left, right) for left, right in zip(config, reference)
            )
        return config == reference
    base_normalized = normalize(base_comparable)
    candidate_normalized = normalize(cand_comparable)
    if base_normalized != candidate_normalized:
        raise ValueError("candidate differs from baseline in a field besides the dApp selector")
    if not subset_matches(normalize(expected_comparable), base_normalized):
        raise ValueError("recorded RA-ENG-005 baseline differs from the paired scenario fields")
    return baseline, candidate


def valid_grant(line: str) -> bool:
    fields = line.rstrip("\n").split(",")
    try:
        return (
            len(fields) == 19 and fields[0] == "APPLIED_GRANT"
            and fields[2] in ("UL", "DL")
            and all(int(fields[index]) >= 0 for index in (1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))
            and bool(fields[18])
        )
    except (ValueError, IndexError):
        return False


def valid_packet_event(line: str) -> bool:
    fields = line.rstrip("\n").split(",")
    try:
        return (
            len(fields) == 9 and fields[0] in ("PACKET_TX", "PACKET_RX")
            and all(int(fields[index]) >= 0 for index in (1, 2, 3, 4, 6, 8))
            and bool(fields[5]) and bool(fields[7])
        )
    except (ValueError, IndexError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True,
                        help="new unique ignored run directory; existing paths are rejected")
    parser.add_argument("--python", type=Path, default=SIM / ".venv/bin/python")
    args = parser.parse_args()
    baseline_config, candidate_config = validate_configs()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise SystemExit(f"refusing to overwrite existing run directory: {output_root}")
    output_root.mkdir(parents=True)
    (output_root / "policy-probe-manifest.json").write_text(json.dumps({
        "mission": "RA-ENG-006", "seed": 11,
        "baseline_config": str(BASELINE_CONFIG.relative_to(ROOT)),
        "baseline_config_sha256": sha256(BASELINE_CONFIG),
        "candidate_config": str(POLICY_CONFIG.relative_to(ROOT)),
        "candidate_config_sha256": sha256(POLICY_CONFIG),
        "changed_factor": "orchestrator.dapp_algo_ue_selection: RoundRobin -> TopKCqi",
        "baseline_reference_run": str(BASELINE_RUN.relative_to(ROOT)),
        "baseline_reference_run_config_sha256": sha256(BASELINE_RUN / "effective-run-config.yaml"),
        "fixed_factors": ["scenario traffic, UE identities, seed, duration, source/drain window, positions, whole-cell LOS, TDD, bandwidth, numerology, k, xApp Bypass, controller periods"],
        "source_sha256": {rel: sha256(IBORAN / rel) for rel in SOURCE_PATHS},
    }, indent=2) + "\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(IBORAN) + os.pathsep + env.get("PYTHONPATH", "")
    python_executable = args.python if args.python.is_absolute() else ROOT / args.python
    notebook = IBORAN / "notebook"
    policy_arms = (("roundrobin", BASELINE_CONFIG, baseline_config),
                   ("topkcqi", POLICY_CONFIG, candidate_config))
    failures = []
    for case, scenario_source, config in policy_arms:
        run_dir = output_root / case
        log_dir = run_dir / "logs"
        analysis_dir = run_dir / "analysis"
        run_dir.mkdir()
        log_dir.mkdir()
        analysis_dir.mkdir()
        shutil.copy2(scenario_source, run_dir / "scenario.yaml")
        case_env = env.copy()
        case_env["IBORAN_RUN_DIR"] = str(run_dir)
        command = [str(python_executable), "iboran_run.py", "--rat_type=NR",
                   "--scenario_config", str((run_dir / "scenario.yaml").resolve())]
        started = time.time()
        metadata = {"case": case, "seed": 11, "command": command,
                    "scenario_sha256": sha256(run_dir / "scenario.yaml"),
                    "started_unix": started}
        (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        with (run_dir / "execution.log").open("w") as stdout:
            result = subprocess.run(command, cwd=CAMPAIGN, env=case_env, stdout=stdout,
                                    stderr=subprocess.STDOUT, check=False)
        metadata["finished_unix"] = time.time()
        metadata["exit_status"] = result.returncode
        if result.returncode != 0:
            failures.append({"case": case, "exit_status": result.returncode})
            (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
            print(f"{case}: exit={result.returncode} output={run_dir}", flush=True)
            continue

        copies = {
            notebook / "logs/runConfig.yaml": run_dir / "effective-run-config.yaml",
            notebook / "logs/kpi.json": log_dir / "kpi.json",
            notebook / ".flowstats/iboran-flowstats.xml": log_dir / "flowstats.xml",
            notebook / "logs/dapp_logs/dAppMacScheduler.log": log_dir / "dapp-decisions.log",
        }
        for source, destination in copies.items():
            if not source.exists() or source.stat().st_mtime < started:
                raise RuntimeError(f"successful run did not create a fresh required artifact: {source}")
            shutil.copy2(source, destination)
        demand_path = log_dir / "mac-demand.csv"
        if not demand_path.exists() or demand_path.stat().st_size == 0:
            raise RuntimeError(f"{case}: successful run did not create a MAC demand trace")

        stdout_path = run_dir / "execution.log"
        mapper = [str(python_executable), str(ROOT / "scripts/map_g1_udp_flows.py"),
                  "--stdout", str(stdout_path), "--flowstats", str(log_dir / "flowstats.xml"),
                  "--output", str(log_dir / "flow-map.csv")]
        subprocess.run(mapper, cwd=ROOT, check=True)

        raw_text = stdout_path.read_text(errors="replace")
        notice = "Max Packets per trace file exceeded\n"
        notice_lines = []
        raw_lines = raw_text.splitlines()
        for index, line in enumerate(raw_lines):
            if "Max Packets per trace file exceeded" in line:
                notice_lines.append({
                    "line": index + 1,
                    "prefix": line.split("Max Packets per trace file exceeded", 1)[0],
                    "continuation": raw_lines[index + 1] if index + 1 < len(raw_lines) else "",
                })
        clean_text = raw_text.replace(notice, "")
        cleaned = analysis_dir / "analysis-stdout-cleaned.log"
        cleaned.write_text(clean_text)
        invalid_after_repair = []
        for index, line in enumerate(clean_text.splitlines(), 1):
            if line.startswith(("PACKET_TX,", "PACKET_RX,")) and not valid_packet_event(line):
                invalid_after_repair.append({"line": index, "kind": "packet", "text": line[:240]})
            elif line.startswith("APPLIED_GRANT,") and not valid_grant(line):
                invalid_after_repair.append({"line": index, "kind": "grant", "text": line[:240]})
        if invalid_after_repair:
            failures.append({"case": case, "error": "malformed telemetry remains after trace-message repair",
                             "invalid_rows": invalid_after_repair})
            metadata["analysis_status"] = "malformed_telemetry"
            (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
            print(f"{case}: telemetry repair validation failed; raw log preserved", flush=True)
            continue
        (analysis_dir / "input-cleanup.json").write_text(json.dumps({
            "raw_stdout": "execution.log", "derived_stdout": "analysis-stdout-cleaned.log",
            "interleaved_notice": "Max Packets per trace file exceeded",
            "interleaved_notice_count": len(notice_lines), "repaired_locations": notice_lines,
            "packet_or_grant_rows_dropped": 0,
            "rule": "remove only the exact interleaved notice and its newline, rejoining the original trace bytes on each side; raw stdout is unchanged",
        }, indent=2) + "\n")
        analyzer = [str(python_executable), str(ROOT / "scripts/analyze_g1_packets.py"),
                    "--stdout", str(cleaned), "--mapping", str(log_dir / "flow-map.csv"),
                    "--config", str(run_dir / "effective-run-config.yaml"),
                    "--output-dir", str(analysis_dir)]
        analyzed = subprocess.run(analyzer, cwd=ROOT, check=False)
        if analyzed.returncode != 0:
            failures.append({"case": case, "error": "packet analyzer failed", "exit_status": analyzed.returncode})
            metadata["analysis_status"] = "failed"
            (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
            print(f"{case}: analysis failed with exit={analyzed.returncode}; raw log preserved", flush=True)
            continue
        metadata["analysis_status"] = "complete"
        metadata["interleaved_notice_count"] = len(notice_lines)
        metadata["source_sha256"] = {rel: sha256(IBORAN / rel) for rel in SOURCE_PATHS}
        (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(f"{case}: exit=0 interleaved_notices={len(notice_lines)} output={run_dir}", flush=True)

    complete = not failures and all((output_root / case / "analysis/ue_packet_metrics.csv").exists()
                                    for case, _, _ in policy_arms)
    (output_root / "exit-summary.json").write_text(json.dumps({
        "complete": complete, "seed": 11, "policies": ["RoundRobin", "TopKCqi"],
        "failures": failures,
    }, indent=2) + "\n")
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
