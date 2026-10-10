"""Copy a genuinely prepared baseline. Never inference, train or create a fake artifact."""
import argparse
import json
from pathlib import Path
import shutil
import hashlib

p=argparse.ArgumentParser();p.add_argument("--prepared",required=True);p.add_argument("--output",required=True);args=p.parse_args()
src=Path(args.prepared).resolve();dst=Path(args.output).resolve();manifest=src/"prepared-artifact.json"
if not manifest.is_file():raise SystemExit("Baseline not materialized: prepared-artifact.json is missing.")
m=json.loads(manifest.read_text())
if m.get("status")!="materialized" or not m.get("files"):raise SystemExit("Baseline is not materialized.")
if dst.exists() or dst.is_relative_to(src) or src.is_relative_to(dst):raise SystemExit("Output must be a new independent directory.")
for name,sha in m["files"].items():
    if not isinstance(name,str) or Path(name).is_absolute() or ".." in Path(name).parts:
        raise SystemExit("Baseline paths must be relative and cannot traverse parents.")
    f=(src/name).resolve()
    if not f.is_relative_to(src) or not f.is_file():
        raise SystemExit("Baseline file verification failed.")
    h=hashlib.sha256()
    with f.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    if h.hexdigest()!=sha:
        raise SystemExit("Baseline file verification failed.")
# Copy only declared files. Unlisted caches or source credentials are not transported.
dst.mkdir(parents=True)
for name in m["files"]:
    target=dst/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/name,target)
shutil.copy2(manifest,dst/"prepared-artifact.json")
print(dst)
