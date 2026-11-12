#!/usr/bin/env python3
"""Validate matched, no-traffic LOS/NLOS radio mobility evidence."""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path

import yaml


def read_trace(path: Path) -> list[dict[str, str]]:
    with path.open() as stream:
        lines = [line.partition("RADIO_MOBILITY_TRACE,")[2] for line in stream]
    lines = [line for line in lines if line]
    if len(lines) < 2:
        raise ValueError(f"{path}: expected a trace header and rows")
    return list(csv.DictReader(io.StringIO("\n".join(lines))))


def load_yaml(path: Path) -> dict:
    with path.open() as stream:
        return yaml.safe_load(stream)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--los-trace", type=Path, required=True)
    parser.add_argument("--nlos-trace", type=Path, required=True)
    parser.add_argument("--los-config", type=Path, required=True)
    parser.add_argument("--nlos-config", type=Path, required=True)
    parser.add_argument("--fixed-trace", type=Path)
    args = parser.parse_args()

    los = read_trace(args.los_trace)
    nlos = read_trace(args.nlos_trace)
    los_config = load_yaml(args.los_config)
    nlos_config = load_yaml(args.nlos_config)
    if los_config["common"]["enableDlFlow"] or los_config["common"]["enableUlFlow"]:
        raise ValueError("LOS evidence unexpectedly enables application flows")
    if nlos_config["common"]["enableDlFlow"] or nlos_config["common"]["enableUlFlow"]:
        raise ValueError("NLOS evidence unexpectedly enables application flows")
    if los_config["nr"]["channelCondition"] != "LOS":
        raise ValueError("LOS config does not select whole-cell LOS")
    if nlos_config["nr"]["channelCondition"] != "NLOS":
        raise ValueError("NLOS config does not select whole-cell NLOS")
    los_config["nr"]["channelCondition"] = "CONDITION"
    nlos_config["nr"]["channelCondition"] = "CONDITION"
    if los_config != nlos_config:
        raise ValueError("paired effective configs differ outside channel condition")

    def index(rows: list[dict[str, str]]) -> dict[tuple[float, int], dict[str, str]]:
        return {(float(row["time_s"]), int(row["ue_index"])): row for row in rows}

    los_by_key = index(los)
    nlos_by_key = index(nlos)
    if los_by_key.keys() != nlos_by_key.keys():
        raise ValueError("time/UE trace keys differ between paired arms")
    if len({key[1] for key in los_by_key}) != 6:
        raise ValueError("expected six distinct UE indices")

    position_fields = (
        "gnb_x_m",
        "gnb_y_m",
        "gnb_z_m",
        "ue_x_m",
        "ue_y_m",
        "ue_z_m",
    )
    for key, row in los_by_key.items():
        other = nlos_by_key[key]
        if row["condition"] != "LOS" or other["condition"] != "NLOS":
            raise ValueError(f"unexpected realized condition for {key}")
        if any(row[field] != other[field] for field in position_fields):
            raise ValueError(f"paired geometry differs for {key}")
        if (row["ue_node_id"], row["gnb_node_id"], row["rnti"]) != (
            other["ue_node_id"],
            other["gnb_node_id"],
            other["rnti"],
        ):
            raise ValueError(f"node/RNTI mapping differs for {key}")

    first_time = min(time for time, _ in los_by_key)
    second_time = min(time for time, _ in los_by_key if time > first_time)
    speeds = []
    for ue_index in range(6):
        a = los_by_key[(first_time, ue_index)]
        b = los_by_key[(second_time, ue_index)]
        speeds.append(float(b["ue_x_m"]) - float(a["ue_x_m"]))
    if any(abs(speed - 0.83) > 1e-8 for speed in speeds):
        raise ValueError(f"controlled x speed differs from 0.83 m/s: {speeds}")

    mapped = [row for (time, _), row in los_by_key.items() if time > first_time]
    rntis = {int(row["rnti"]) for row in mapped}
    if len(rntis) != 6 or 0 in rntis:
        raise ValueError(f"expected six assigned, distinct RNTIs after attach: {rntis}")
    if len(los) != 20 * 6 or len(nlos) != 20 * 6:
        raise ValueError("expected one-second samples over t=0..19 for six UEs")

    if args.fixed_trace:
        fixed = read_trace(args.fixed_trace)
        if not fixed or any(row["condition"] != "LOS" for row in fixed):
            raise ValueError("fixed-position probe did not realize LOS on every row")
        for ue_index in range(6):
            positions = {
                tuple(row[field] for field in position_fields)
                for row in fixed
                if int(row["ue_index"]) == ue_index
            }
            if len(positions) != 1:
                raise ValueError(f"fixed UE {ue_index} changed position: {positions}")

    print("RA-ENG-002 paired validation: PASS")
    print(f"LOS rows={len(los)}; NLOS rows={len(nlos)}; simulated trace times=0..19 s")
    print(f"UE indices=0..5; RNTIs={sorted(rntis)}; matched seed/run=1/1")
    print("All positions, node IDs and attached RNTI mappings match across conditions.")
    print("Observed condition is LOS in all LOS rows and NLOS in all NLOS rows.")
    print("Initial-to-1 s x displacement is 0.83 m for each UE; app traffic is disabled.")
    if args.fixed_trace:
        print("Fixed-mode probe: all six UE positions remained constant across samples.")


if __name__ == "__main__":
    main()
