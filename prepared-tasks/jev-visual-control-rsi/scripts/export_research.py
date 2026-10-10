#!/usr/bin/env python3
"""Export ALL public source/data/answers/seeds from the frozen artifact inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);args=p.parse_args()
out=args.output.resolve()
if out==ROOT or ROOT in out.parents:raise SystemExit("research export must be outside the source package")
if out.exists() and any(out.iterdir()):raise SystemExit("output must be absent or empty")
manifest=json.loads((ROOT/"ARTIFACT_MANIFEST.json").read_text())
out.mkdir(parents=True,exist_ok=True)
for rel,info in manifest["files"].items():
    src=ROOT/rel
    if hashlib.sha256(src.read_bytes()).hexdigest()!=info["sha256"]:raise ValueError("source hash mismatch: "+rel)
    dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
shutil.copy2(ROOT/"ARTIFACT_MANIFEST.json",out/"ARTIFACT_MANIFEST.json")
print(json.dumps({"files":len(manifest["files"])+1,"all_evaluation_records_solutions_seeds":True,"encrypted":False,"model_calls":0}))
