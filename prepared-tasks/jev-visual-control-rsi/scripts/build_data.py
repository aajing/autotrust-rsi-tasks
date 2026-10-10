#!/usr/bin/env python3
"""Materialize or read-only replay the complete CPU scene/certificate package."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import secrets
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from visual_control.contract import COUNTS,FAMILIES,TIERS,canonical
from visual_control.scenes import seed_for,make_scene
from visual_control.authoring import certify


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true");args=parser.parse_args()
    authority=ROOT/"data/authoring_seed.json"
    if not authority.exists():
        if args.check:raise ValueError("authoring seed absent")
        authority.write_text(json.dumps({"master_hex":secrets.token_hex(32),"scope":"public_inspection_and_reproduction"},indent=2)+"\n")
        authority.chmod(0o644)
    master=json.loads(authority.read_text())["master_hex"]
    records={};certificates={};seen=set();seeds=set();attempt_total=0
    allowed={"train":set(range(6)),"development":{6,7},"evaluation":{8,9}}
    for split,count in COUNTS.items():
        records[split]=[];certificates[split]=[]
        for family in FAMILIES:
            for tier in TIERS:
                accepted=0
                for attempt in range(10000):
                    attempt_total+=1
                    seed=seed_for(master,split,family,tier,attempt)
                    record=make_scene(family,tier,seed)
                    geometry=record["geometry_sha256"]
                    if int(geometry[:8],16)%10 not in allowed[split] or geometry in seen:continue
                    certificate=certify(record)
                    if seed in seeds:raise ValueError("duplicate seed")
                    seen.add(geometry);seeds.add(seed)
                    record["split"]=split;records[split].append(record);certificates[split].append(certificate)
                    accepted+=1
                    if accepted==count:break
                if accepted!=count:raise ValueError("fixed authoring cap exhausted")
        print(split,len(records[split]),"certified",flush=True)
    manifest={"schema":2,"protocol":"jev-visual-control-cpu-v2-public","scene_count":224,
              "model_inference_performed":False,"model_performance_claimed":False,
              "distribution":"all records, certificates and seed public; inspection permitted; per-scene solution lookup in the controller prohibited",
              "renderer":"Pillow CPU orthographic reference; optional MuJoCo rendering is not the certified scoring lane",
              "partition":"int(geometry_sha256[:8],16)%10 train0..5 development6..7 evaluation8..9",
              "unique_geometries":len(seen),"unique_seeds":len(seeds),"generated_attempts":attempt_total,"files":{}}
    products={}
    for split in COUNTS:
        for kind,rows in [("scenes",records[split]),("certificates",certificates[split])]:
            rel=f"data/{split}/{kind}.jsonl";raw="".join(canonical(row)+"\n" for row in rows).encode()
            products[rel]=raw;manifest["files"][rel]={"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"rows":len(rows)}
        manifest.setdefault("cells",{})[split]=dict(sorted(collections.Counter(r["family"]+"/"+r["tier"] for r in records[split]).items()))
    products["data/manifest.json"]=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode()
    for rel,raw in products.items():
        p=ROOT/rel
        if args.check:
            if not p.is_file() or p.read_bytes()!=raw:raise ValueError("frozen byte mismatch: "+rel)
        else:
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            p.chmod(0o644)
    print(json.dumps({"status":"verified" if args.check else "materialized","scenes":224,"references_succeeded":224,"model_calls":0}))

if __name__=="__main__":main()
