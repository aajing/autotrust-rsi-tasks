#!/usr/bin/env python3
"""Meaningful CPU contracts, including adversarial parser and coverage checks."""
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
from policy import admit, Budget, choose_action, FEATURES
from runtime_adapter import FrozenModelAdapter, ModelRuntimeUnavailable

manifest = json.loads((task.ROOT / "data/manifest.json").read_text())
for name, sha in manifest["generators"].items():
    assert hashlib.sha256((task.ROOT/name).read_bytes()).hexdigest() == sha
for f in manifest["files"]:
    raw = (task.ROOT / f["path"]).read_bytes()
    assert len(raw) == f["bytes"] and hashlib.sha256(raw).hexdigest() == f["sha256"]
seeds = json.loads((task.ROOT / "data/public/seeds.json").read_text())
assert manifest["visibility"] == "fully_public"
assert not (task.ROOT/"data/private").exists()
regenerated, groups = task.construct(seeds)
seen = set()
for g in groups:
    assert g["group"] not in seen
    seen.add(g["group"])
summary = {}
for split, per_family in task.COUNTS.items():
    rp, gp = task.paths(split)
    records, gold = task.read_jsonl(rp), task.read_jsonl(gp)
    assert (records, gold) == regenerated[split]
    assert len(records) == len(gold) == per_family * 5
    assert all(sum(r["family"] == f for r in records) == per_family for f in task.FAMILIES)
    assert all(set(r) == {"id", "family", "input"} for r in records)
    assert all(sum(g["family"] == f and g["difficulty"] == d for g in gold) == per_family // 2
               for f in task.FAMILIES for d in ("direct", "compositional"))
    predictions = [{"id": g["id"], "answer": g["answer"]} for g in gold]
    result = task.score(records, gold, predictions)
    assert result["score"] == 100 and result["correct"] == len(records)
    wrong = [{"id": g["id"], "answer": None} for g in gold]
    assert task.score(records, gold, wrong)["score"] == 0
    assert task.score(records, gold, predictions[:-1])["status"] == "unscored"
    assert task.score(records, gold, predictions[:-1] + [predictions[0]])["status"] == "unscored"
    summary[split] = {"records": len(records), "oracle_fixture_score": 100, "all_wrong_score": 0}
    for r, g in zip(records, gold):
        if r["family"] == "sql":
            assert not task.check_answer(r, g, {"sql": "DROP TABLE products"})
            assert not task.check_answer(r, g, {"sql": "SELECT * FROM products; SELECT * FROM orders"})
        elif r["family"] == "schedule":
            bad = {"schedule": [{"job": x["id"], "start": -1} for x in r["input"]["jobs"]]}
            assert not task.check_answer(r, g, bad)
        elif r["family"] == "workflow":
            assert not task.check_answer(r, g, {"actions": g["answer"]["actions"][:-1]})
        elif r["family"] == "python":
            assert type(g["answer"]["value"]) is int
try:
    task.run_python("import os\nresult = 1")
    raise AssertionError("unsafe Python accepted")
except ValueError:
    pass
for config in ("b0", "short_only", "fixed_reconsideration"):
    admit(json.loads((task.ROOT / "configs" / (config + ".json")).read_text()))
fixed=json.loads((task.ROOT/"configs/fixed_reconsideration.json").read_text())
assert choose_action(fixed,{"confidence":1.0}) == "reconsider_1024"
mlp={"version":1,"kind":"mlp","feature_names":list(FEATURES),"mean":[0]*len(FEATURES),"scale":[1]*len(FEATURES),
     "layers":[{"weight":[[0]*len(FEATURES)],"bias":[0]}, {"weight":[[1]],"bias":[0]}, {"weight":[[0] for _ in range(5)],"bias":[0,0,1,0,0]}]}
admit(mlp)
assert choose_action(mlp,{f:0 for f in FEATURES}) == "reconsider_512"
bad = json.loads((task.ROOT / "configs/b0.json").read_text()); bad["python_hook"] = "evil.py"
try:
    admit(bad)
    raise AssertionError("unknown hook accepted")
except ValueError:
    pass
b = Budget({"calls": 3, "tokens": 100})
assert b.reserve({"calls": 1, "tokens": 20}, {"calls": 2, "tokens": 40})
assert not b.reserve({"calls": 1, "tokens": 50}, {"calls": 2, "tokens": 40})
assert any(len(j["after"]) == 2 for rs, _ in regenerated.values() for r in rs if r["family"] == "schedule" for j in r["input"]["jobs"])
assert any("HAVING" in g["answer"].get("sql", "") for _, gs in regenerated.values() for g in gs)
assert any("after" in t for rs, _ in regenerated.values() for r in rs if r["family"] == "workflow" for t in r["input"]["targets"])
try:
    FrozenModelAdapter()
    raise AssertionError("model stub did not fail closed")
except ModelRuntimeUnavailable:
    pass
print(json.dumps({"status": "cpu_contracts_passed", "splits": summary,
                  "semantic_groups": len(groups), "gpu_or_model_run": False,
                  "official_runtime_validated": False}, indent=2))
