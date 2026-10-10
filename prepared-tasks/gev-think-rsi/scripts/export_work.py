#!/usr/bin/env python3
"""Export the public research workspace, including every evaluation answer."""
import argparse
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
p = argparse.ArgumentParser(); p.add_argument("--output", required=True); args = p.parse_args()
out = Path(args.output).resolve()
if out.exists(): raise SystemExit("Output must not exist; refusing to merge into an existing Work tree.")
out.mkdir(parents=True)
allow = ["task.py", "policy.py", "runtime_adapter.py", "configs", "prompts", "data", "scripts", "LICENSE", "README.md", "proposal.md", "evidence"]
for name in allow:
    source, target = task.ROOT/name, out/name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir(): shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else: shutil.copy2(source, target)
for name in ("evaluation.jsonl", "evaluation_gold.jsonl", "seeds.json", "groups.jsonl"):
    assert (out/"data/public"/name).is_file()
print(json.dumps({"work_export":str(out),"all_evaluation_inputs_answers_seeds_included":True,
                  "evaluation_reserved_from_fitting_by_protocol":False,"evaluation_informed_fitting_and_selection_allowed":True,"runtime_validated":False}))
