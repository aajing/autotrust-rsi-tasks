#!/usr/bin/env python3
"""Public construction inventory, including all evaluation records and solutions."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
paths=[]
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.name=="ARTIFACT_MANIFEST.json" or "__pycache__" in path.parts or path.suffix==".pyc":continue
    if "work_ledgers" in path.parts or path.name=="judge_attempts.jsonl":continue
    paths.append(path)
manifest={"schema":1,"task":"jev-visual-control-rsi","distribution":"public unencrypted task bundle; researcher inspection allowed; execution interface restricted",
          "model_inference_performed":False,"official_review_submission_performed":False,"public_distribution_authorized":True,
          "files":{str(path.relative_to(ROOT)):{"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths}}
raw=json.dumps(manifest,indent=2,sort_keys=True)+"\n"
target=ROOT/"ARTIFACT_MANIFEST.json"
if args.check:
    if target.read_text()!=raw:raise SystemExit("artifact inventory/hash mismatch")
else:target.write_text(raw)
print(json.dumps({"status":"verified" if args.check else "frozen","files":len(paths)}))
