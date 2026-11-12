#!/usr/bin/env python3
"""Materialize one validated, isolated G1 radio/mobility run configuration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
IBORAN_MODEL = REPO / "simulator/ns-3.48/contrib/iboran/model"
sys.path.insert(0, str(IBORAN_MODEL))

from utils.config_store import ConfigStore, DEFAULT_CONFIG_PATH  # noqa: E402


def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, default=REPO / "configs/scenarios/g1-radio-mobility-los.yaml")
    parser.add_argument("--condition", choices=("LOS", "NLOS"))
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.scenario.open() as stream:
        scenario = yaml.safe_load(stream) or {}
    with DEFAULT_CONFIG_PATH.open() as stream:
        defaults = yaml.safe_load(stream) or {}

    effective = deep_merge(defaults, scenario)
    if args.condition:
        effective["nr"]["channelCondition"] = args.condition
    effective["common"]["rngRun"] = args.seed
    validated = ConfigStore(**effective)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as stream:
        yaml.safe_dump(validated.model_dump(mode="json"), stream, sort_keys=False)


if __name__ == "__main__":
    main()
