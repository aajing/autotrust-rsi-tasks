#!/usr/bin/env python3
"""Runs real local inference ONLY when the operator explicitly invokes it."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from visual_control.runtime import evaluate

p=argparse.ArgumentParser()
p.add_argument("--work",type=Path,required=True)
p.add_argument("--endpoint",required=True)
p.add_argument("--split",choices=("train","development","evaluation"),default="development")
p.add_argument("--worker-user")
p.add_argument("--work-id",help="stable operator-assigned candidate ID for the shared two-hour Work ledger")
p.add_argument("--output",type=Path,required=True)
args=p.parse_args()
if args.output.exists(): raise SystemExit("Refusing to overwrite an existing result")
try:
    result=evaluate(ROOT,args.work,args.endpoint,args.split,args.worker_user,args.work_id)
except Exception as exc:
    result={"status":"unscored","error_type":type(exc).__name__,"reason":str(exc)}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
print(json.dumps(result))
if result["status"]=="unscored": raise SystemExit(2)
