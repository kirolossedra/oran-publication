#!/usr/bin/env python3
"""Rebuild paired stock-policy analyses from preserved raw run directories."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

from run_g1_stock_policy_probe import valid_grant, valid_packet_event


ROOT = Path(__file__).resolve().parents[1]
SIM_PYTHON = ROOT / "simulator/ns-3.48/.venv/bin/python"
NOTICE = "Max Packets per trace file exceeded\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def config_identity(path: Path) -> tuple[dict, str]:
    with path.open() as stream:
        config = yaml.safe_load(stream)
    policy = config["orchestrator"]["dapp_algo_ue_selection"]
    config_without_policy = json.loads(json.dumps(config))
    config_without_policy["orchestrator"].pop("dapp_algo_ue_selection")
    return config_without_policy, policy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roundrobin", type=Path, required=True,
                        help="preserved raw RoundRobin case directory")
    parser.add_argument("--topkcqi", type=Path, required=True,
                        help="preserved raw TopKCqi case directory")
    parser.add_argument("--output-root", type=Path, required=True,
                        help="new, nonexistent directory for derived reanalysis")
    args = parser.parse_args()

    base, base_policy = config_identity(args.roundrobin / "effective-run-config.yaml")
    cand, cand_policy = config_identity(args.topkcqi / "effective-run-config.yaml")
    if base != cand or (base_policy, cand_policy) != ("RoundRobin", "TopKCqi"):
        raise SystemExit("preserved runs are not the expected RoundRobin/TopKCqi paired configs")
    out = args.output_root.resolve()
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing reanalysis root: {out}")
    out.mkdir(parents=True)
    failures = []
    for case, raw, case_policy in (("roundrobin", args.roundrobin.resolve(), base_policy),
                                   ("topkcqi", args.topkcqi.resolve(), cand_policy)):
        case_dir = out / case
        logs = case_dir / "logs"
        analysis = case_dir / "analysis"
        logs.mkdir(parents=True)
        analysis.mkdir()
        for name in ("scenario.yaml", "effective-run-config.yaml", "run-metadata.json"):
            shutil.copy2(raw / name, case_dir / name)
        shutil.copy2(raw / "logs/mac-demand.csv", logs / "mac-demand.csv")
        shutil.copy2(raw / "logs/flowstats.xml", logs / "flowstats.xml")
        shutil.copy2(raw / "logs/dapp-decisions.log", logs / "dapp-decisions.log")

        raw_stdout = raw / "execution.log"
        text = raw_stdout.read_text(errors="replace")
        cleaned_text = text.replace(NOTICE, "")
        cleaned = analysis / "analysis-stdout-cleaned.log"
        cleaned.write_text(cleaned_text)
        invalid = []
        for line_number, line in enumerate(cleaned_text.splitlines(), 1):
            if line.startswith(("PACKET_TX,", "PACKET_RX,")) and not valid_packet_event(line):
                invalid.append({"line": line_number, "kind": "packet", "text": line[:240]})
            elif line.startswith("APPLIED_GRANT,") and not valid_grant(line):
                invalid.append({"line": line_number, "kind": "grant", "text": line[:240]})
        if invalid:
            failures.append({"case": case, "invalid_rows_after_repair": invalid})
            continue

        mapper = [str(SIM_PYTHON), str(ROOT / "experiment-scripts/map_udp_flows.py"),
                  "--stdout", str(raw_stdout), "--flowstats", str(logs / "flowstats.xml"),
                  "--output", str(logs / "flow-map.csv")]
        mapped = subprocess.run(mapper, cwd=ROOT, check=False)
        if mapped.returncode:
            failures.append({"case": case, "mapper_exit_status": mapped.returncode})
            continue
        analyzer = [str(SIM_PYTHON), str(ROOT / "experiment-scripts/analyze_packet_events.py"),
                    "--stdout", str(cleaned), "--mapping", str(logs / "flow-map.csv"),
                    "--config", str(case_dir / "effective-run-config.yaml"),
                    "--output-dir", str(analysis)]
        analyzed = subprocess.run(analyzer, cwd=ROOT, check=False)
        if analyzed.returncode:
            failures.append({"case": case, "analyzer_exit_status": analyzed.returncode})
            continue
        notices = []
        for index, line in enumerate(text.splitlines(), 1):
            if "Max Packets per trace file exceeded" in line:
                notices.append({"line": index, "prefix": line.split(NOTICE.strip(), 1)[0]})
        (analysis / "input-cleanup.json").write_text(json.dumps({
            "raw_stdout": str(raw_stdout), "raw_stdout_sha256": sha256(raw_stdout),
            "derived_stdout": "analysis-stdout-cleaned.log",
            "interleaved_notice": NOTICE.strip(), "interleaved_notice_count": len(notices),
            "repaired_lines": notices, "packet_or_grant_rows_dropped": 0,
            "rule": "remove only the exact AnimationInterface notice and newline, rejoining original trace bytes; raw stdout remains unchanged",
        }, indent=2) + "\n")
        (case_dir / "reanalysis-provenance.json").write_text(json.dumps({
            "raw_run_directory": str(raw),
            "raw_stdout_sha256": sha256(raw_stdout),
            "effective_run_config_sha256": sha256(raw / "effective-run-config.yaml"),
            "flowstats_sha256": sha256(raw / "logs/flowstats.xml"),
            "policy": case_policy,
        }, indent=2) + "\n")

    complete = not failures and all((out / case / "analysis/ue_packet_metrics.csv").exists()
                                    for case in ("roundrobin", "topkcqi"))
    (out / "reanalysis-summary.json").write_text(json.dumps({
        "complete": complete, "pair": ["RoundRobin", "TopKCqi"],
        "effective_configs_equal_outside_policy": True, "failures": failures,
    }, indent=2) + "\n")
    if not complete:
        return 1
    print(f"reprocessed_cases=2 policies={base_policy},{cand_policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
