#!/usr/bin/env python3
"""Resumable integrated six-UE campaign runner; raw artifacts are append-only by attempt."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml


ROOT = Path(__file__).resolve().parents[3]
SIM = ROOT / "simulator/ns-3.48"
IBORAN = SIM / "contrib/iboran"
BASE = IBORAN / "model/iboran_campaign/iboranConfig.yaml"
SPEC_PATH = Path(__file__).resolve().parents[1] / "config/g1-integrated-campaign.json"
SPEC = json.loads(SPEC_PATH.read_text())
CAMPAIGN_ID = SPEC["campaign_id"]
RUNS = ROOT / "simulator/runs" / CAMPAIGN_ID
SEEDS = tuple(SPEC["seeds"])
CHANNELS = tuple(SPEC["channels"])
MOBILITIES = tuple(SPEC["mobility_modes"])
LOADS = tuple(SPEC["loads"])
POLICIES = tuple(SPEC["policies"])
RATES = SPEC["traffic_bps_per_ue_per_direction"]

# Outcome-sensitive files, including the policy code omitted from the previous provenance record.
OUTCOME_SOURCE_PATHS = (
    SIM / "contrib/iboran/model/iboran_application/iboran-application.cc",
    SIM / "contrib/iboran/model/iboran_mac_scheduler/iboran-nr-mac-scheduler.cc",
    SIM / "contrib/iboran/model/iboran_ran_environment/iboran-ran-common.cc",
    SIM / "contrib/iboran/model/iboran_ran_environment/iboran-nr-environment.cc",
    SIM / "contrib/iboran/model/iboran_ran_environment/iboran-ran-params.cc",
    SIM / "contrib/iboran/model/iboran_ran_environment/iboran-ran-params.h",
    SIM / "contrib/iboran/model/utils/config_store.py",
    SIM / "contrib/iboran/model/iboran_controller/iboran_dapp_mac_scheduler.py",
    SIM / "contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_round_robin.py",
    SIM / "contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection_top_k.py",
    SIM / "contrib/iboran/model/iboran_controller/iboran_dapp_algos/dapp_algo_ue_selection.py",
)


def outcome_source_hashes() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): sha256(p) for p in OUTCOME_SOURCE_PATHS}


def attempt_number(path: Path) -> int:
    return int(path.name.split("-", 1)[1])


def has_data_rows(path: Path, columns: set[str]) -> bool:
    if not path.is_file():
        return False
    with path.open(encoding="utf-8", errors="replace") as f:
        fields = set(f.readline().strip().split(","))
        return columns.issubset(fields) and bool(f.readline().strip())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def plan() -> list[dict]:
    cells = []
    for channel, mobility, load, policy, seed in itertools.product(
        CHANNELS, MOBILITIES, LOADS, POLICIES, SEEDS
    ):
        cell = {
            "channel": channel,
            "mobility": mobility,
            "load": load,
            "policy": policy,
            "seed": seed,
            "directions": ["DL", "UL"],
        }
        cell["cell_id"] = "-".join(
            [channel, mobility, load, policy.lower(), f"seed{seed:02d}"]
        )
        cells.append(cell)
    return cells


def pilot_block(cells: list[dict]) -> list[dict]:
    """Select one seed's 2x2x2 channel/load/policy block at stationary mobility."""
    pilot_seed = SEEDS[0]
    pilot_loads = ("light", "contending")
    selected = [
        cell for cell in cells
        if cell["mobility"] == "stationary"
        and cell["load"] in pilot_loads
        and cell["seed"] == pilot_seed
    ]
    if len(selected) != 8:
        raise RuntimeError(f"expected 8 pilot cells, planned {len(selected)}")
    return selected


def write_once(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content)


def attempt_config(base_cfg: dict, cell: dict, path: Path) -> dict:
    cfg = copy.deepcopy(base_cfg)
    common = cfg["common"]
    offered = RATES[cell["load"]]
    offered_dl, offered_ul = offered["DL"], offered["UL"]
    common.update(
        {
            "simTime": SPEC["simulation"]["duration_s"],
            "ueNum": 6,
            "xnbNum": 1,
            "enableDlFlow": True,
            "enableUlFlow": True,
            "dlTxRepeat": 0,
            "ulTxRepeat": 0,
            "dlPacketSize": SPEC["simulation"]["packet_payload_bytes"],
            "ulPacketSize": SPEC["simulation"]["packet_payload_bytes"],
            "dlBitRate": offered_dl,
            "ulBitRate": offered_ul,
            "perUeDlBitRate": [offered_dl] * 6,
            "perUeUlBitRate": [offered_ul] * 6,
            "receiverDrainTime": SPEC["simulation"]["receiver_drain_s"],
            "enableNetAnim": False,
            "rngRun": cell["seed"],
            "channelConditionMode": cell["channel"],
            "channelConditionTargetUe": 6,
            "mobilityMode": cell["mobility"],
        }
    )
    cfg["orchestrator"].update(
        {
            "k": 1,
            "dapp_algo_ue_selection": cell["policy"],
            "xapp_algo_rbg_bounding": "Bypass",
            "save_dapp_log": True,
            "verbose": False,
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return cfg


def latest_success(cell_dir: Path, expected_hashes: dict[str, str] | None = None) -> bool:
    """Only reuse measured successes from the exact current implementation."""
    if expected_hashes is None:
        expected_hashes = outcome_source_hashes()
    for attempt in sorted(cell_dir.glob("attempt-*"), key=attempt_number, reverse=True):
        status = attempt / "exit-status.txt"
        if not status.exists() or status.read_text().strip() != "0":
            continue
        try:
            metadata = json.loads((attempt / "run-metadata.json").read_text())
            if metadata.get("packet_measurement_schema") != "serialized-app-header-v1":
                continue
            if metadata.get("source_sha256") != expected_hashes:
                continue
            if not (attempt / "logs/kpi.json").is_file():
                continue
            if not has_data_rows(attempt / "logs/packet-events.csv",
                                 {"event", "time_ns", "ue_index", "direction", "sequence", "tx_time_ns", "bytes"}):
                continue
            if not has_data_rows(attempt / "logs/mac-grants.csv",
                                 {"time_ns", "rnti", "direction", "rbg_count", "mcs"}):
                continue
            if not has_data_rows(attempt / "logs/mac-demand.csv",
                                 {"time_ns", "rnti", "direction", "buffer_bytes", "cqi"}):
                continue
            return True
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Run first N planned cells (diagnostics only)")
    parser.add_argument(
        "--pilot-block", action="store_true",
        help="Run the predeclared first-seed 2x2x2 channel/load/policy block at stationary mobility",
    )
    parser.add_argument("--python", default=str(SIM / ".venv/bin/python"))
    parser.add_argument("--campaign-root", type=Path, default=RUNS)
    args = parser.parse_args()
    if args.pilot_block and args.limit:
        parser.error("--pilot-block and --limit cannot be combined")
    campaign_root = args.campaign_root.resolve()
    campaign_root.mkdir(parents=True, exist_ok=True)
    base_copy = campaign_root / "frozen-base-config.yaml"
    if not base_copy.exists():
        shutil.copy2(BASE, base_copy)
    write_once(campaign_root / "experiment-spec.json", json.dumps(SPEC, indent=2) + "\n")
    base_cfg = yaml.safe_load(base_copy.read_text())
    cells = plan()
    planned = campaign_root / "planned-matrix.json"
    write_once(planned, json.dumps({
        "campaign_id": CAMPAIGN_ID,
        "factors": {"channel": CHANNELS, "mobility": MOBILITIES, "load": LOADS,
                    "policy": POLICIES, "seed": SEEDS, "directions_measured_together": True},
        "spec_sha256": sha256(SPEC_PATH),
        "traffic_bps_per_ue_per_direction": RATES,
        "planned_simulation_runs": len(cells),
        "cells": cells,
    }, indent=2) + "\n")
    extension_cells = [cell for cell in cells if cell["load"] in ("dl-contending", "ul-contending")]
    if extension_cells:
        write_once(campaign_root / "directional-load-extension.json", json.dumps({
            "predeclared_before_extension_runs": True,
            "rationale": "isolate downlink-only and uplink-only contention while measuring both outcomes",
            "added_planned_runs": len(extension_cells),
            "cells": extension_cells,
            "traffic_bps_per_ue_per_direction": {
                "dl-contending": RATES["dl-contending"],
                "ul-contending": RATES["ul-contending"],
            },
        }, indent=2) + "\n")
    manifest = campaign_root / "attempts.jsonl"
    if args.pilot_block:
        work = pilot_block(cells)
        pilot_seed = SEEDS[0]
        pilot_loads = ("light", "contending")
        write_once(campaign_root / "pilot-block-selection.json", json.dumps({
            "predeclared_before_formal_repetitions": True,
            "seed": pilot_seed,
            "mobility": "stationary",
            "channel": list(CHANNELS),
            "load": list(pilot_loads),
            "policy": list(POLICIES),
            "directions_measured_together": ["DL", "UL"],
            "cell_ids": [cell["cell_id"] for cell in work],
        }, indent=2) + "\n")
    else:
        work = cells[:args.limit] if args.limit else cells
    current_source_hashes = outcome_source_hashes()
    for index, cell in enumerate(work, 1):
        if outcome_source_hashes() != current_source_hashes:
            raise RuntimeError("Outcome source code changed during campaign; stop before mixing implementations")
        cell_dir = campaign_root / "cells" / cell["cell_id"]
        cell_dir.mkdir(parents=True, exist_ok=True)
        if latest_success(cell_dir, current_source_hashes):
            print(f"[{index}/{len(work)}] SKIP already successful {cell['cell_id']}", flush=True)
            continue
        attempts = list(cell_dir.glob("attempt-*"))
        next_attempt = max((attempt_number(p) for p in attempts), default=0) + 1
        attempt = cell_dir / f"attempt-{next_attempt:02d}"
        attempt.mkdir(parents=True)
        cfg_path = attempt / "scenario.yaml"
        effective = attempt_config(base_cfg, cell, cfg_path)
        (attempt / "cell.json").write_text(json.dumps(cell, indent=2) + "\n")
        environment = os.environ.copy()
        environment["IBORAN_RUN_DIR"] = str(attempt)
        environment["IBORAN_CONFIG_PATH"] = str(cfg_path)
        environment["PYTHONPATH"] = str(IBORAN) + os.pathsep + environment.get("PYTHONPATH", "")
        command = [
            args.python, "iboran_run.py", "--rat_type=NR",
            f"--rng_run={cell['seed']}",
            f"--dapp_algo_ue_selection={cell['policy']}",
            "--xapp_algo_rbg_bounding=Bypass",
            "--save_dapp_log=true", "--verbose=false",
        ]
        metadata = {
            "cell": cell,
            "attempt": str(attempt),
            "command": command,
            "packet_measurement_schema": "serialized-app-header-v1",
            "config_sha256": sha256(cfg_path),
            "source_sha256": current_source_hashes,
            "started_unix": time.time(),
        }
        (attempt / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(f"[{index}/{len(work)}] RUN {cell['cell_id']} -> {attempt}", flush=True)
        with (attempt / "execution.log").open("w") as log:
            result = subprocess.run(command, cwd=IBORAN / "model/iboran_campaign", env=environment,
                                    stdout=log, stderr=subprocess.STDOUT, check=False)
        (attempt / "exit-status.txt").write_text(f"{result.returncode}\n")
        metadata["finished_unix"] = time.time()
        metadata["exit_status"] = result.returncode
        (attempt / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        with manifest.open("a") as out:
            out.write(json.dumps({"cell_id": cell["cell_id"], "attempt": str(attempt),
                                  "exit_status": result.returncode}) + "\n")
        print(f"[{index}/{len(work)}] EXIT {result.returncode} {cell['cell_id']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
