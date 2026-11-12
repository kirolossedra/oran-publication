#!/usr/bin/env python3
"""Run paired target-UE LOS->NLOS->LOS and all-LOS O-RAN control probes.

This is an ENGINEERING test: numerical values remain unset until PI selection.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "simulator/ns-3.48"
IBORAN = SIM / "contrib/iboran"
SPEC = ROOT / "configs/los-nlos-transition.json"
BASE = IBORAN / "model/iboran_campaign/iboranConfig.yaml"
MANIFEST = ROOT / "simulator/overrides/iboran/SHA256SUMS"


def verify(spec):
    topo, tr, rates, radio, orch, sim = [spec[k] for k in (
        "topology", "transition", "traffic_bps", "radio", "orchestrator", "simulation")]
    if topo["gnb_count"] != 1 or topo["ue_count"] != 6:
        raise ValueError("Requires 1 gNB and 6 UEs")
    if not 1 <= topo["target_ue_index"] <= 6:
        raise ValueError("Invalid target UE index")
    if topo["target_velocity_mps"] != 1 or not topo["background_stationary"]:
        raise ValueError("Pinned target-controlled-linear mode moves target only at 1 m/s")
    a,b=tr["nlos_start_s"],tr["nlos_end_s"]
    if a is None or b is None or not 0 < a < b < sim["duration_s"]:
        raise ValueError("PI must define 0 < transition start < end < duration")
    if radio["bandwidth_hz"] is None or radio["bandwidth_hz"] <= 0:
        raise ValueError("PI must select radio bandwidth after verifying effective capacity")
    for label, group in rates.items():
        for direction in ("UL","DL"):
            value=group[direction]
            if type(value) is not int or not 0 < value <= 4294967295:
                raise ValueError("PI must select positive traffic rate: "+label+"."+direction)
    if type(orch["k"]) is not int or not 1 <= orch["k"] <= 6:
        raise ValueError("PI must select dApp k, 1..6; k=1 can starve")
    if not orch["dapp_selectors"] or not set(orch["dapp_selectors"]) <= {
        "RoundRobin","GreedyPropFairness"}:
        raise ValueError("Unknown source-verified dApp choice")
    if not orch["xapp_bounds"] or not set(orch["xapp_bounds"]) <= {"Bypass","Clamp"}:
        raise ValueError("Unknown source-verified xApp choice")
    if spec["channel_modes"] != ["all-los","ue-transition"]:
        raise ValueError("Paired baseline and transition required")
    if not spec["seeds"] or len(set(spec["seeds"])) != len(spec["seeds"]):
        raise ValueError("Unique, nonempty seeds required")


def plan(spec):
    return [
        {"channel":chan, "dapp":dapp, "xapp":xapp, "seed":seed,
         "cell_id":f"{chan}-{dapp.lower()}-{xapp.lower()}-seed{seed}"}
        for chan,dapp,xapp,seed in itertools.product(
            spec["channel_modes"],spec["orchestrator"]["dapp_selectors"],
            spec["orchestrator"]["xapp_bounds"],spec["seeds"])
    ]


def config_for(base,spec,cell):
    out=copy.deepcopy(base)
    target=spec["topology"]["target_ue_index"]-1
    rates=spec["traffic_bps"]
    ul=[rates["background_per_ue"]["UL"]]*6
    dl=[rates["background_per_ue"]["DL"]]*6
    ul[target]=rates["target"]["UL"]
    dl[target]=rates["target"]["DL"]
    tr=spec["transition"]
    sim=spec["simulation"]
    out["rat_type"]="NR"
    out["common"].update({
        "simTime":sim["duration_s"],"ueNum":6,"xnbNum":1,
        "channelConditionMode":cell["channel"],"channelConditionTargetUe":target+1,
        "channelTransitionStartS":tr["nlos_start_s"],"channelTransitionEndS":tr["nlos_end_s"],
        "mobilityMode":"target-controlled-linear","rngRun":cell["seed"],
        "perUeDlBitRate":dl,"perUeUlBitRate":ul,"dlBitRate":dl[0],"ulBitRate":ul[0],
        "enableDlFlow":True,"enableUlFlow":True,"dlTxRepeat":0,"ulTxRepeat":0,
        "dlPacketSize":sim["packet_payload_bytes"],"ulPacketSize":sim["packet_payload_bytes"],
        "dlUseUdp":True,"ulUseUdp":True,"receiverDrainTime":sim["receiver_drain_s"],
        "enableNetAnim":False})
    out["nr"].update({
        "centralFrequency":spec["radio"]["center_frequency_hz"],
        "bandwidth":spec["radio"]["bandwidth_hz"],
        "numerology":spec["radio"]["numerology"]})
    out["orchestrator"].update({
        "k":spec["orchestrator"]["k"],
        "dapp_algo_ue_selection":cell["dapp"],
        "xapp_algo_rbg_bounding":cell["xapp"],
        "save_dapp_log":True,"verbose":False})
    return out


def check_transition(log,cell,spec):
    records=[]
    for line in log.splitlines():
        if line.startswith("CHANNEL_TRANSITION,"):
            values=dict(x.split("=",1) for x in line.split(",")[1:] if "=" in x)
            records.append((float(values["time_s"]),int(values["ue_index"]),values["condition"]))
    if cell["channel"]=="ue-transition":
        expected=[
            (float(spec["transition"]["nlos_start_s"]),
             spec["topology"]["target_ue_index"],"NLOS"),
            (float(spec["transition"]["nlos_end_s"]),
             spec["topology"]["target_ue_index"],"LOS")]
        if len(records)!=2 or any(
            abs(a[0]-b[0])>1e-5 or a[1:]!=b[1:] for a,b in zip(records,expected)):
            raise ValueError(f"Incorrect actual channel model boundary trace: {records}")
    elif records:
        raise ValueError("all-los control has unexpected transition events")
    if "CHANNEL_STATE," not in log:
        raise ValueError("No per-UE channel snapshots found")


def run_one(spec,cell,base,root,python):
    directory=root/"cells"/cell["cell_id"]
    directory.mkdir(parents=True,exist_ok=True)
    n=max([int(p.name.split("-")[1]) for p in directory.glob("attempt-*")
           if re.fullmatch(r"attempt-\d+",p.name)]+[0])+1
    attempt=directory/f"attempt-{n:02d}"
    attempt.mkdir()
    config=attempt/"scenario.yaml"
    config.write_text(yaml.safe_dump(config_for(base,spec,cell),sort_keys=False))
    (attempt/"cell.json").write_text(json.dumps(cell,indent=2)+"\n")
    command=[
        python,"iboran_run.py","--rat_type=NR",f"--rng_run={cell['seed']}",
        f"--dapp_algo_ue_selection={cell['dapp']}",
        f"--xapp_algo_rbg_bounding={cell['xapp']}",
        "--save_dapp_log=true","--verbose=false"]
    env=os.environ.copy()
    env.update({"IBORAN_RUN_DIR":str(attempt),"IBORAN_CONFIG_PATH":str(config),
                "PYTHONPATH":str(IBORAN)+os.pathsep+env.get("PYTHONPATH","")})
    metadata={"cell":cell,"command":command,
              "spec_sha256":hashlib.sha256((root/"experiment-spec.json").read_bytes()).hexdigest(),
              "scenario_sha256":hashlib.sha256(config.read_bytes()).hexdigest(),
              "source_manifest_sha256":hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
              "started_unix":time.time()}
    (attempt/"run-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    with (attempt/"execution.log").open("w") as output:
        exitcode=subprocess.run(command,cwd=IBORAN/"model/iboran_campaign",
                                env=env,stdout=output,stderr=subprocess.STDOUT).returncode
    error=None
    if exitcode==0:
        try:
            check_transition((attempt/"execution.log").read_text(errors="replace"),cell,spec)
        except ValueError as exc:
            error=str(exc)
            exitcode=2
    (attempt/"exit-status.txt").write_text(str(exitcode)+"\n")
    metadata.update({"finished_unix":time.time(),"exit_status":exitcode,
                     "transition_audit_error":error})
    (attempt/"run-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return {"cell_id":cell["cell_id"],"attempt":str(attempt),"exit_status":exitcode,
            "transition_audit_error":error}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec",type=Path,default=SPEC)
    p.add_argument("--python",default=str(SIM/".venv/bin/python"))
    p.add_argument("--campaign-root",type=Path)
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--limit",type=int,default=0)
    args=p.parse_args()
    spec=json.loads(args.spec.read_text())
    cells=plan(spec)
    if args.plan_only:
        print(json.dumps({"planned_cells":cells,
                          "unselected_scientific_fields":["transition times","radio bandwidth",
                          "target/peer UL/DL bitrates","scheduler k"]},indent=2))
        return 0
    verify(spec)
    if not BASE.is_file() or not Path(args.python).is_file() or not MANIFEST.is_file():
        raise SystemExit("Pinned WSL dependencies/overrides missing; restore simulator first")
    from prepare_los_nlos_transition import verify_installed
    mismatches = verify_installed()
    if mismatches:
        raise SystemExit("Simulator sources do not match pinned transition implementation: " +
                         ", ".join(mismatches) + "; run prepare_los_nlos_transition.py --apply-overrides")
    root=(args.campaign_root or ROOT/"simulator/runs"/spec["campaign_id"]).resolve()
    root.mkdir(parents=True,exist_ok=True)
    frozen=json.dumps(spec,indent=2)+"\n"
    frozen_path=root/"experiment-spec.json"
    if frozen_path.exists() and frozen_path.read_text()!=frozen:
        raise SystemExit("Campaign parameters changed: use a NEW root, preserve previous runs")
    if not frozen_path.exists():
        frozen_path.write_text(frozen)
    if args.limit<0:
        raise SystemExit("Negative limit not allowed")
    base=yaml.safe_load(BASE.read_text())
    results=[]
    for cell in cells[:args.limit] if args.limit else cells:
        status=run_one(spec,cell,base,root,args.python)
        results.append(status)
        with (root/"attempts.jsonl").open("a") as output:
            output.write(json.dumps(status)+"\n")
        print(f"{cell['cell_id']}: exit {status['exit_status']}",flush=True)
    return 1 if any(x["exit_status"] for x in results) else 0


if __name__=="__main__":
    raise SystemExit(main())
