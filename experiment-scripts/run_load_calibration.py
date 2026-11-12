#!/usr/bin/env python3
"""Run append-only, per-UE G1 load-calibration probes on the pinned simulator."""

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
SCENARIOS = ROOT / "configs/scenarios/calibration"
CASES = ("target-only", "low-six", "dl-contending", "ul-contending")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_case(case: str) -> tuple[Path, dict]:
    path = SCENARIOS / f"{case}.yaml"
    cfg = yaml.safe_load(path.read_text())
    common = cfg["common"]
    flows = common["ueTraffic"]
    if common["ueNum"] != 6 or common["rngRun"] != 11:
        raise ValueError(f"{case}: expected six UEs and fixed seed 11")
    if common["mobilityMode"] != "Fixed" or cfg["nr"]["channelCondition"] != "LOS":
        raise ValueError(f"{case}: the calibration control conditions changed")
    indices = [int(flow["ueIndex"]) for flow in flows]
    if len(indices) != len(set(indices)) or any(i not in range(6) for i in indices):
        raise ValueError(f"{case}: UE flow identities are invalid or duplicated")
    for flow in flows:
        if flow["startTime"] != 1.0 or flow["stopTime"] != 8.0 or flow["sinkStopTime"] != 9.0:
            raise ValueError(f"{case}: source/drain window differs from the paired design")
    by_ue = {int(flow["ueIndex"]): flow for flow in flows}
    if case == "target-only" and set(by_ue) != {0}:
        raise ValueError("target-only case must configure only UE 0")
    if case != "target-only" and set(by_ue) != set(range(6)):
        raise ValueError(f"{case}: expected explicit traffic for all six UEs")
    if case == "low-six" and any(
        flow[direction] != 20_000 for flow in flows
        for direction in ("ulBitRate", "dlBitRate")
    ):
        raise ValueError("low-six case must offer 20 kbps per UE per direction")
    if case in ("dl-contending", "ul-contending"):
        high = "dlBitRate" if case.startswith("dl") else "ulBitRate"
        low = "ulBitRate" if high == "dlBitRate" else "dlBitRate"
        for ue, flow in by_ue.items():
            expected = 20_000 if ue == 0 else 6_000_000
            if flow[high] != expected or flow[low] != 20_000:
                raise ValueError(f"{case}: unexpected per-UE {high}/{low} at UE {ue}")
    return path, cfg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True,
                        help="new, nonexistent raw run directory; existing paths are rejected")
    parser.add_argument("--case", choices=CASES, action="append",
                        help="case(s) to run; default runs the four predeclared probes")
    parser.add_argument("--python", type=Path, default=SIM / ".venv/bin/python")
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise SystemExit(f"refusing to overwrite existing run directory: {output_root}")
    cases = args.case or list(CASES)
    prepared = [(case, *load_case(case)) for case in cases]
    output_root.mkdir(parents=True, exist_ok=False)
    (output_root / "run-manifest.json").write_text(json.dumps({
        "mission": "RA-ENG-005",
        "seed": 11,
        "cases": cases,
        "scenario_sha256": {case: sha256(path) for case, path, _ in prepared},
        "source_sha256": {
            "dapp_mac_scheduler": sha256(IBORAN / "model/iboran_controller/iboran_dapp_mac_scheduler.py"),
            "ran_common": sha256(IBORAN / "model/iboran_ran_environment/iboran-ran-common.cc"),
            "nr_environment": sha256(IBORAN / "model/iboran_ran_environment/iboran-nr-environment.cc"),
            "nr_mac_scheduler": sha256(IBORAN / "model/iboran_mac_scheduler/iboran-nr-mac-scheduler.cc"),
        },
    }, indent=2) + "\n")

    failed = []
    for case, scenario_path, config in prepared:
        run_dir = output_root / case
        run_dir.mkdir()
        log_dir = run_dir / "logs"
        log_dir.mkdir()
        shutil.copy2(scenario_path, run_dir / "scenario.yaml")
        env = os.environ.copy()
        env["IBORAN_RUN_DIR"] = str(run_dir)
        env["PYTHONPATH"] = str(IBORAN) + os.pathsep + env.get("PYTHONPATH", "")
        # Preserve the venv's symlink path; resolving it discards pyvenv.cfg context.
        python_executable = args.python if args.python.is_absolute() else ROOT / args.python
        command = [str(python_executable), "iboran_run.py", "--rat_type=NR",
                   "--scenario_config", str(scenario_path.resolve())]
        started = time.time()
        metadata = {
            "case": case, "seed": config["common"]["rngRun"],
            "command": command, "scenario_sha256": sha256(scenario_path),
            "started_unix": started,
        }
        (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        with (run_dir / "execution.log").open("w") as stdout:
            result = subprocess.run(command, cwd=CAMPAIGN, env=env, stdout=stdout,
                                    stderr=subprocess.STDOUT, check=False)
        metadata["finished_unix"] = time.time()
        metadata["exit_status"] = result.returncode
        (run_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

        notebook = IBORAN / "notebook"
        if result.returncode == 0:
            copies = {
                notebook / "logs/runConfig.yaml": run_dir / "effective-run-config.yaml",
                notebook / "logs/kpi.json": log_dir / "kpi.json",
                notebook / ".flowstats/iboran-flowstats.xml": log_dir / "flowstats.xml",
            }
            for source, destination in copies.items():
                if source.exists() and source.stat().st_mtime >= started:
                    shutil.copy2(source, destination)
        demand = log_dir / "mac-demand.csv"
        if not demand.exists():
            failed.append(f"{case}: missing mac-demand.csv")
        if result.returncode != 0:
            failed.append(f"{case}: exit {result.returncode}")
        print(f"{case}: exit={result.returncode} output={run_dir}", flush=True)

    (output_root / "exit-summary.json").write_text(json.dumps({
        "cases": cases, "failures": failed, "complete": not failed,
    }, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
