# ARCHIVED HISTORICAL SCRIPT. DO NOT EXECUTE: the dated source-export layout no longer exists.
#!/usr/bin/env python3
"""Back up, verify, and apply the approved G1 campaign source overrides once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "campaigns/20261111-g1-integrated-v2/source-overrides"
IBORAN = ROOT / "simulator/ns-3.48/contrib/iboran"
RUN_ROOT = ROOT / "simulator/logs/RA-ENG-007-20261112"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    run_root = RUN_ROOT
    provenance_path = run_root / "source-application.json"
    if provenance_path.exists():
        raise SystemExit(f"refusing to replace existing source application record: {provenance_path}")

    manifest = PACKAGE / "SHA256SUMS"
    records = []
    for line in manifest.read_text().splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip()
        source_rel = Path(relative)
        source = PACKAGE / source_rel
        target = IBORAN / source_rel
        if not source.is_file() or not target.is_file():
            raise SystemExit(f"missing override or installed source: {relative}")
        actual_package = sha256(source)
        if actual_package != expected:
            raise SystemExit(f"package source hash mismatch for {relative}: {actual_package}")
        records.append((expected, source_rel, source, target))
    if not records:
        raise SystemExit("source override manifest is empty")

    backup_root = run_root / "source-backup"
    installed_root = run_root / "source-installed"
    if backup_root.exists() or installed_root.exists():
        raise SystemExit(f"refusing to overwrite source evidence under {run_root}")
    backup_root.mkdir(parents=True)
    installed_root.mkdir(parents=True)

    before = []
    for expected, relative, source, target in records:
        backup = backup_root / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
        before.append({"path": str(relative), "sha256": sha256(target)})

    for expected, relative, source, target in records:
        shutil.copy2(source, target)
        actual = sha256(target)
        if actual != expected:
            raise SystemExit(f"installed source hash mismatch for {relative}: {actual}")
        archived = installed_root / relative
        archived.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, archived)

    try:
        ns3_commit = subprocess.check_output(
            ["git", "-C", str(ROOT / "simulator/ns-3.48"), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        ns3_commit = "unavailable"
    payload = {
        "approved_protocol": "existing 160-cell v2 matrix",
        "timestamp_unix": time.time(),
        "ns3_checkout_commit": ns3_commit,
        "override_manifest": str(manifest.relative_to(ROOT)),
        "override_count": len(records),
        "pre_application_sha256": before,
        "post_application_sha256": [
            {"path": str(relative), "sha256": sha256(target)}
            for _, relative, _, target in records
        ],
    }
    provenance_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"applied={len(records)} ns3_commit={ns3_commit} evidence={provenance_path}")


if __name__ == "__main__":
    main()
