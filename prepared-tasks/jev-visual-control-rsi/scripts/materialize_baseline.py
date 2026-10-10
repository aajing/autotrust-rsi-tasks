#!/usr/bin/env python3
"""Create a fixed B0 execution artifact. Full public research assets are exported
separately by export_research.py. No model or evaluation is invoked."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);args=p.parse_args()
if args.output.exists() and any(args.output.iterdir()): raise SystemExit("output must be absent or empty")
args.output.mkdir(parents=True,exist_ok=True)
files={"visual_control/baseline.py":"controller.py","visual_control/candidate_worker.py":"candidate_worker.py",
       "configs/baseline.json":"baseline.json","configs/budget.json":"budget.json",
       "configs/source_manifest.json":"source_manifest.json","PROTOCOL.md":"PROTOCOL.md"}
manifest={}
for source,dest in files.items():
    shutil.copy2(ROOT/source,args.output/dest)
    manifest[dest]=hashlib.sha256((args.output/dest).read_bytes()).hexdigest()
(args.output/"work_manifest.json").write_text(json.dumps({"schema":1,"files":manifest,"contains_realized_scene_data":False,"public_research_assets_available":True,"restriction":"execution interface, not confidentiality"},indent=2)+"\n")
print(json.dumps({"materialized":str(args.output),"files":len(files),"model_calls":0,"episodes_run":0}))
