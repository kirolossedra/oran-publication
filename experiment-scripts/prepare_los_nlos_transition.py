#!/usr/bin/env python3
"""Verify/apply reviewed ib-ORAN source overrides without running legacy G1 experiments."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
IBORAN=ROOT/"simulator/ns-3.48/contrib/iboran"
NS3=ROOT/"simulator/ns-3.48"
OVERRIDES=ROOT/"simulator/overrides/iboran"
MANIFEST=OVERRIDES/"SHA256SUMS"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries():
    items=[]
    for row in MANIFEST.read_text().splitlines():
        if not row.strip():
            continue
        expected, relative=row.split(maxsplit=1)
        src=(OVERRIDES/relative).resolve()
        dst=(IBORAN/relative).resolve()
        if not src.is_relative_to(OVERRIDES.resolve()) or not dst.is_relative_to(IBORAN.resolve()):
            raise ValueError("Unsafe manifest path: "+relative)
        if not src.is_file() or sha(src)!=expected:
            raise ValueError("Committed source or manifest hash mismatch: "+relative)
        items.append((relative,expected,src,dst))
    if not items:
        raise ValueError("No pinned overrides")
    return items


def verify_installed():
    differing=[]
    for relative,expected,_,dst in entries():
        if not dst.is_file() or sha(dst)!=expected:
            differing.append(relative)
    return differing


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-overrides",action="store_true",
                        help="Explicitly backup and install the pinned source overrides")
    parser.add_argument("--build",action="store_true",
                        help="Run unit tests and build the pinned ns-3 ib-ORAN NR target")
    parser.add_argument("--jobs",type=int,default=2)
    args=parser.parse_args()
    if args.jobs < 1:
        parser.error("Positive --jobs required")
    changed=verify_installed()
    if changed:
        print("Pinned sources requiring sync:",", ".join(changed),flush=True)
        if not args.apply_overrides:
            raise SystemExit("Mismatched local simulator: review then pass --apply-overrides")
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup=ROOT/"simulator/source-backups"/("los-nlos-"+stamp)
        backup.mkdir(parents=True,exist_ok=False)
        for rel,_,src,dst in entries():
            if rel not in changed:
                continue
            if not dst.is_file():
                raise SystemExit("Missing pinned upstream file; bootstrap before syncing: "+str(dst))
            old=backup/rel
            old.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(dst,old)
        for rel,_,src,dst in entries():
            if rel in changed:
                shutil.copy2(src,dst)
        print("Backed up original source to",backup,flush=True)
    after=verify_installed()
    if after:
        raise SystemExit("Source pin verification failed: "+str(after))
    print("All ib-ORAN source overrides match the pinned manifest",flush=True)
    if args.build:
        subprocess.run([sys.executable,"-m","unittest","discover","-s",
                        str(ROOT/"tests"),"-v"],cwd=ROOT,check=True)
        subprocess.run(["./ns3","build","ns3iboran_nr","-j",str(args.jobs)],
                       cwd=NS3,check=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
