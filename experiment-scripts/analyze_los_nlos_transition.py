#!/usr/bin/env python3
"""Measure LOS->NLOS->LOS phase outcomes by packet TRANSMISSION time.

Do not mistake received-only P99 for complete reliability; report missing-by-stop.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
from statistics import mean
from run_los_nlos_transition import check_transition


def phase(seconds,start,end):
    return "pre-los" if seconds < start else (
        "nlos-window" if seconds < end else "post-los")


def percentile(values,q):
    if not values:
        return None
    values=sorted(values)
    index=(len(values)-1)*q
    lower=int(index)
    upper=min(lower+1,len(values)-1)
    return values[lower]+(values[upper]-values[lower])*(index-lower)


def link(direction):
    return {"0":"DL","1":"UL","DL":"DL","UL":"UL"}[str(direction).upper()]


def csvfile(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def analyze(attempt,spec):
    cell=json.loads((attempt/"cell.json").read_text())
    check_transition((attempt/"execution.log").read_text(errors="replace"),cell,spec)
    start=float(spec["transition"]["nlos_start_s"])
    end=float(spec["transition"]["nlos_end_s"])
    stop=float(spec["simulation"]["duration_s"])
    sent={}
    received={}
    owners=defaultdict(set)
    for row in csvfile(attempt/"logs/packet-events.csv"):
        ue=int(row["ue_index"])
        direction=link(row["direction"])
        seq=int(row["sequence"])
        key=(ue,direction,seq)
        rnti=int(row.get("rnti") or 0)
        if rnti:
            owners[(rnti,direction)].add(ue)
        if row["event"].upper()=="TX":
            if key in sent:
                raise ValueError(f"Duplicate transmitted sequence: {attempt} {key}")
            sent[key]=row
        elif row["event"].upper()=="RX":
            if key not in received or int(row["time_ns"])<int(received[key]["time_ns"]):
                received[key]=row
    outcome=defaultdict(lambda:{"tx":0,"rx":0,"bytes":0,"delays":[],"late":0})
    for key,row in sent.items():
        ue,direction,_=key
        tx_seconds=int(row["tx_time_ns"])/1e9
        bucket=phase(tx_seconds,start,end)
        item=outcome[(ue,direction,bucket)]
        item["tx"]+=1
        if key in received:
            rx_seconds=int(received[key]["time_ns"])/1e9
            if tx_seconds<=rx_seconds<=stop+1e-6:
                item["rx"]+=1
                item["bytes"]+=int(row["bytes"])
                item["delays"].append((rx_seconds-tx_seconds)*1000)
                item["late"]+=int(phase(rx_seconds,start,end)!=bucket)
    grants=defaultdict(list)
    unmapped_grants=0
    for grant in csvfile(attempt/"logs/mac-grants.csv"):
        grant_dir=link(grant["direction"])
        matches=owners.get((int(grant["rnti"]),grant_dir),set())
        if len(matches)!=1:
            unmapped_grants+=1
            continue
        grant_ue=next(iter(matches))
        grant_phase=phase(int(grant["time_ns"])/1e9,start,end)
        grants[(grant_ue,grant_dir,grant_phase)].append(grant)
    cqi=defaultdict(list)
    for sample in csvfile(attempt/"logs/mac-demand.csv"):
        direction=link(sample["direction"])
        associated=owners.get((int(sample["rnti"]),direction),set())
        if len(associated)==1:
            ue=next(iter(associated))
            bucket=phase(int(sample["time_ns"])/1e9,start,end)
            cqi[(ue,direction,bucket)].append(float(sample["cqi"]))
    windows={"pre-los":(0,start),"nlos-window":(start,end),"post-los":(end,stop)}
    output=[]
    for ue in range(1,7):
        for direction in ("UL","DL"):
            for bucket,(begin,finish) in windows.items():
                item=outcome[(ue,direction,bucket)]
                samples=cqi[(ue,direction,bucket)]
                applied=grants[(ue,direction,bucket)]
                channel="NLOS" if (cell["channel"]=="ue-transition" and
                                   ue==spec["topology"]["target_ue_index"] and
                                   bucket=="nlos-window") else "LOS"
                output.append({
                    **cell,"ue_index":ue,"direction":direction,
                    "phase":bucket,"expected_channel":channel,
                    "window_seconds":finish-begin,
                    "tx_packets":item["tx"],"rx_packets":item["rx"],
                    "not_received_by_stop":item["tx"]-item["rx"],
                    "delivery_fraction":item["rx"]/item["tx"] if item["tx"] else None,
                    "tx_cohort_delivered_mbps":item["bytes"]*8/((finish-begin)*1e6),
                    "p95_received_ms":percentile(item["delays"],0.95),
                    "p99_received_ms":percentile(item["delays"],0.99),
                    "p99_received_count":len(item["delays"]),
                    "received_after_phase":item["late"],
                    "mean_mac_reported_cqi":mean(samples) if samples else None,
                    "cqi_samples":len(samples),
                    "applied_grant_count":len(applied),
                    "allocated_prbs":sum(int(x.get("prb_count") or 0) for x in applied),
                    "granted_transport_bytes":sum(int(x.get("tbs_bytes") or 0) for x in applied),
                    "mean_grant_mcs":mean([float(x["mcs"]) for x in applied]) if applied else None,
                    "unmapped_grant_count_run":unmapped_grants
                })
    return output


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    spec=json.loads((args.campaign_root/"experiment-spec.json").read_text())
    rows=[]
    for cell in sorted((args.campaign_root/"cells").iterdir()):
        success=[x for x in sorted(cell.glob("attempt-*")) if
                 (x/"exit-status.txt").is_file() and
                 (x/"exit-status.txt").read_text().strip()=="0"]
        if success:
            rows+=analyze(success[-1],spec)
    if not rows:
        raise SystemExit("No successful, transition-verified runs available")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise SystemExit("Refusing to overwrite prior derived results")
    with args.output.open("w",newline="") as output:
        w=csv.DictWriter(output,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} per-phase/UE/direction rows; scientific inference requires PI review")


if __name__=="__main__":
    main()
