#!/usr/bin/env python3
"""Work-only training calibration from real supplied train predictions.

Does not call the model or assert authentic prediction provenance.
Never invoke from Solution or Judge.
"""
import argparse
import json
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
from policy import admit, calibrate
p = argparse.ArgumentParser(); p.add_argument("--predictions", required=True); p.add_argument("--output", required=True); args = p.parse_args()
_, gp = task.paths("train"); labels = {g["id"]: g["complete"] for g in task.read_jsonl(gp)}
predictions = task.read_jsonl(args.predictions)
seen = set(); data = []
for row in predictions:
    rid, prob = row.get("id"), row.get("p_complete")
    if not isinstance(rid,str) or rid not in labels or rid in seen or type(prob) not in (int,float) or not math.isfinite(prob) or not 0<=prob<=1:
        raise SystemExit("Only unique training IDs and finite probabilities in [0,1] are permitted.")
    seen.add(rid); data.append((prob,labels[rid]))
if not data: raise SystemExit("No training predictions.")
choices = []
for a in (0.25,0.5,0.75,1.0,1.25,1.5,2.0,3.0,4.0):
    for b in (-1.0,-0.75,-0.5,-0.25,0.0,0.25,0.5,0.75):
        config={"kind":"affine_clip","a":a,"b":b}
        loss=sum((calibrate(prob,config)-y)**2 for prob,y in data)/len(data)
        choices.append((loss,abs(a-1)+abs(b),a,b))
loss,_,a,b=min(choices)
policy=json.loads((task.ROOT/"configs/b0.json").read_text()); policy["calibration"]={"kind":"affine_clip","a":a,"b":b}; admit(policy)
Path(args.output).write_text(json.dumps(policy,indent=2)+"\n")
print(json.dumps({"training_rows":len(data),"training_brier":loss,"model_run":False,"prediction_provenance_checked":False}))
