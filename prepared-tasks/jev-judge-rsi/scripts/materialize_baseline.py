#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
from policy import admit
p = argparse.ArgumentParser()
p.add_argument("--baseline", choices=["b0", "b1"], default="b0")
p.add_argument("--output", required=True)
args = p.parse_args()
source = task.ROOT / "configs" / (args.baseline+".json")
admit(json.loads(source.read_text()))
out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, out/"judge_policy.json")
print("Materialized judge_policy.json only. No training, inference or evaluation; fitted B2 does not exist.")
