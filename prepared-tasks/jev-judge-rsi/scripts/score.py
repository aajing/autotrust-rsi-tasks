#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
p = argparse.ArgumentParser(description="CPU diagnostic; not a model run or official Judge.")
p.add_argument("--predictions", required=True)
p.add_argument("--split", choices=list(task.BATCH_COUNTS), default="evaluation")
args = p.parse_args()
try:
    rp, gp = task.paths(args.split)
    manifest=json.loads((task.ROOT/"data/manifest.json").read_text())
    commitments={f["path"]:f["sha256"] for f in manifest["files"]}
    for path in (rp,gp):
        if hashlib.sha256(path.read_bytes()).hexdigest() != commitments.get(str(path.relative_to(task.ROOT))):
            raise ValueError("evaluation asset hash mismatch")
    result = task.score(task.read_jsonl(rp), task.read_jsonl(gp), task.read_jsonl(args.predictions))
except (OSError, ValueError) as exc:
    result = {"status": "unscored", "reason": str(exc)}
print(json.dumps(result, indent=2))
sys.exit(0 if result["status"] == "diagnostic_complete" else 2)
