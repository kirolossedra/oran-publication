#!/usr/bin/env python3
"""Plot offered rate and delivered goodput by UE for UL and DL calibration probes."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite nonempty output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with args.summary.open(newline="") as stream:
        rows = list(csv.DictReader(stream))

    cases = ["target-only", "low-six", "dl-contending", "ul-contending"]
    labels = ["Target only", "Low six UE", "DL contending", "UL contending"]
    colors = ["#666666", "#4c78a8", "#f58518", "#54a24b"]
    width = 0.19
    for direction in ("DL", "UL"):
        fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
        ue_indices = sorted({int(row["ue_index"]) for row in rows})
        x = np.arange(len(ue_indices), dtype=float)
        for offset, (case, label, color) in enumerate(zip(cases, labels, colors)):
            values, offered = [], []
            for ue in ue_indices:
                match = next((row for row in rows if row["case"] == case
                              and row["direction"] == direction
                              and int(row["ue_index"]) == ue), None)
                values.append(float(match["delivered_goodput_bps"]) / 1e6 if match else np.nan)
                offered.append(float(match["configured_rate_bps"]) / 1e6 if match else np.nan)
            xpos = x + (offset - (len(cases) - 1) / 2) * width
            ax.bar(xpos, values, width=width, color=color, label=label)
            ax.scatter(xpos, offered, marker="_", s=100, linewidths=2, color="black", zorder=4)
        ax.set_xticks(x, [f"UE {ue}" for ue in ue_indices])
        ax.set_ylabel("Mbps")
        ax.set_title(f"{direction}: configured offer and delivered UDP goodput")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(ncols=2, loc="upper left")
        ax.text(0.99, 0.02, "Bars: received goodput; black ticks: configured offer",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
        fig.savefig(args.output_dir / f"g1-load-calibration-{direction.lower()}.png", dpi=180)
        plt.close(fig)


if __name__ == "__main__":
    main()
