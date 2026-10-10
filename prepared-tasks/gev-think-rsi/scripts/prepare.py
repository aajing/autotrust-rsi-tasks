#!/usr/bin/env python3
"""Reproduce the fully public corpus, gold, seeds and provenance; no model calls."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task

seed_path = task.ROOT / "data/public/seeds.json"
seed_path.parent.mkdir(parents=True, exist_ok=True)
seeds = {"train": "gev-think-rsi-train-public-v2", "dev": "gev-think-rsi-dev-public-v2",
         "evaluation": "gev-think-rsi-evaluation-public-v2"}
seed_path.write_text(json.dumps(seeds, indent=2)+"\n")
outputs, groups = task.construct(seeds)
for split, (records, gold) in outputs.items():
    rp, gp = task.paths(split)
    task.write_jsonl(rp, records); task.write_jsonl(gp, gold)
task.write_jsonl(task.ROOT / "data/public/groups.jsonl", groups)
files = []
for path in sorted((task.ROOT / "data/public").rglob("*")):
    if not path.is_file(): continue
    raw = path.read_bytes()
    f = {"path": str(path.relative_to(task.ROOT)), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if path.suffix == ".jsonl": f["records"] = len(raw.splitlines())
    files.append(f)
manifest = {"version": 2, "visibility": "fully_public", "evaluation_reserved_from_fitting_by_protocol": True,
            "generators": {name: hashlib.sha256((task.ROOT/name).read_bytes()).hexdigest() for name in ("task.py",)},
            "families": list(task.FAMILIES), "counts": {s: len(v[0]) for s, v in outputs.items()},
            "semantic_groups": len(groups), "seed_file": "data/public/seeds.json",
            "files": files, "data_license": "CC0-1.0", "gpu_executed": False}
(task.ROOT / "data/manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
print(json.dumps({"prepared": manifest["counts"], "groups": len(groups), "all_answers_public": True, "gpu_executed": False}))
