#!/usr/bin/env python3
"""Sample and run ONE new public-support scene; owner-side, real JEV required."""
import argparse
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from visual_control.authoring import certify
from visual_control.budget import WorkBudget
from visual_control.contract import FAMILIES,TIERS
from visual_control.model_client import ModelClient
from visual_control.runtime import run_episode,worker_command
from visual_control.scenes import make_scene,seed_for
p=argparse.ArgumentParser()
p.add_argument("--work",type=Path,required=True);p.add_argument("--work-id",required=True)
p.add_argument("--endpoint",required=True);p.add_argument("--family",choices=FAMILIES,required=True)
p.add_argument("--tier",choices=TIERS,required=True);p.add_argument("--worker-user")
args=p.parse_args()
budget=WorkBudget(ROOT/"data/work_ledgers",args.work_id);index=budget.charge_new_episode()
master=json.loads((ROOT/"data/authoring_seed.json").read_text())["master_hex"]
reserved={json.loads(line)["geometry_sha256"] for split in ("train","development","evaluation")
          for line in (ROOT/"data"/split/"scenes.jsonl").read_text().splitlines()}
for attempt in range(10000):
    seed=seed_for(master,"exploration/"+args.work_id,args.family,args.tier,index*10000+attempt)
    record=make_scene(args.family,args.tier,seed)
    if int(record["geometry_sha256"][:8],16)%10 < 6 and record["geometry_sha256"] not in reserved:
        certify(record);break
else:raise ValueError("fixed eligible-scene cap exhausted")
command=worker_command(args.work,ROOT/"data",args.worker_user)
broker=ModelClient(args.endpoint,time.monotonic()+budget.remaining_seconds,20000,budget.charge_call)
event=run_episode(record,command,str(args.work.resolve()),broker)
print(json.dumps({k:v for k,v in event.items() if k!="id"}))
