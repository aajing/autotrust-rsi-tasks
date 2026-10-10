#!/usr/bin/env python3
"""CPU contract tests: executable gold, coverage, Brier and public provenance."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import task
from policy import admit, calibrate, Budget
from runtime_adapter import FrozenModelAdapter, ModelRuntimeUnavailable

manifest = json.loads((task.ROOT/"data/manifest.json").read_text())
for name, sha in manifest["generators"].items(): assert hashlib.sha256((task.ROOT/name).read_bytes()).hexdigest() == sha
for f in manifest["files"]:
    data = (task.ROOT/f["path"]).read_bytes()
    assert len(data) == f["bytes"] and hashlib.sha256(data).hexdigest() == f["sha256"]
seeds = json.loads((task.ROOT/"data/public/seeds.json").read_text())
assert manifest["visibility"] == "fully_public"
assert not (task.ROOT/"data/private").exists()
regenerated, groups, media = task.construct(seeds)
assert len({g["group"] for g in groups}) == len(groups) == 864
assert all(len(g["ids"]) == 1 for g in groups)
expected={name for images in media.values() for name in images}
assert {p.name for p in (task.ROOT/"data/public/media").glob("*.png")} == expected
summary = {}
allowed = {"request", "context", "transcript", "artifacts", "images"}
for split, groups_per_family in task.BATCH_COUNTS.items():
    rp, gp = task.paths(split)
    records, gold = task.read_jsonl(rp), task.read_jsonl(gp)
    assert (records, gold) == regenerated[split]
    assert len(records) == len(gold) == 6*8*groups_per_family
    for family in task.FAMILIES:
        rows = [g for g in gold if g["family"] == family]
        assert len(rows) == 8*groups_per_family
        assert sum(g["complete"] for g in rows) == 4*groups_per_family
        for fail in task.FAILURES: assert sum(g["failure_subtype"] == fail for g in rows) == groups_per_family
    for r, g in zip(records, gold):
        assert set(r) == {"id", "family", "input"} and set(r["input"]) == allowed
        assert type(g["complete"]) is int and task.verify(r["family"], g["world"]) == bool(g["complete"])
        assert len(r["input"]["transcript"]) <= 24 and len(r["input"]["images"]) <= 2
        assert not ({"complete", "world", "failure_subtype", "group", "seed", "gold"} & set(r["input"]))
        for image in r["input"]["images"]:
            blob = (rp.parent/image["path"]).read_bytes()
            assert blob.startswith(b"\x89PNG\r\n\x1a\n") and struct.unpack(">II", blob[16:24]) == (768,768)
    perfect = [{"id": g["id"], "p_complete": g["complete"], "evidence": [], "diagnosis": ""} for g in gold]
    assert task.score(records, gold, perfect)["score"] == 100
    # A tiny error, including one whose square underflows, is not exact gold.
    negative = next(i for i, p in enumerate(perfect) if p["p_complete"] == 0)
    for epsilon in (1e-10, 1e-200):
        almost = [dict(p) for p in perfect]
        almost[negative]["p_complete"] = epsilon
        assert task.score(records, gold, almost)["score"] == math.nextafter(100.0, 0.0)
    half = [dict(p, p_complete=0.5) for p in perfect]
    assert task.score(records, gold, half)["score"] == 0
    inverted = [dict(p, p_complete=1-p["p_complete"]) for p in perfect]
    assert task.score(records, gold, inverted)["brier"] == 1
    assert task.score(records, gold, perfect[:-1])["status"] == "unscored"
    assert task.score(records, gold, perfect[:-1]+[perfect[0]])["status"] == "unscored"
    malformed = [dict(p, p_complete=True) for p in perfect]
    assert task.score(records, gold, malformed)["invalid_verdicts"] == len(records)
    badref = [dict(p, evidence=[{"kind":"image","image":99,"box":[0,0,1,1]}]) for p in perfect]
    assert task.score(records, gold, badref)["invalid_verdicts"] == len(records)
    summary[split] = {"records":len(records),"perfect_oracle_fixture":100,"constant_half_score":0,"actual_gold_recomputed":True,"inexact_probability_cannot_score_100":True}
# Regression: these domain values are legitimate successes, not failure-only cues.
all_gold = [g for _, gs in regenerated.values() for g in gs]
positive_settings = [g["world"]["persisted"] for g in all_gold if g["family"] == "settings" and g["complete"]]
assert any(x["theme"] == "SYSTEM" for x in positive_settings)
assert any(x["digest"] == "MONTHLY" for x in positive_settings)
assert any(x["timezone"] == "UTC-1" for x in positive_settings)
for g in all_gold:
    if g["family"] == "settings":
        x = g["world"]["persisted"]
        assert x["theme"] in task.THEMES and x["timezone"] in task.TIMEZONES
        assert "digest" not in x or x["digest"] in task.DIGESTS
        assert "digest_hour" not in x or x["digest_hour"] in range(24)
    if g["family"] == "document":
        x = g["world"]["artifact"]
        assert "invoice" not in x or x["invoice"].startswith("INV-")
        assert "recipient" not in x or x["recipient"].split("-")[0] in {"CEDAR","MAPLE","PINE","BIRCH"}
positive_orders = [g["world"]["actual_order"] for g in all_gold if g["family"] == "browser" and g["complete"]]
assert {x["status"] for x in positive_orders} == {"DRAFT","SUBMITTED"}
assert {x["payment"] for x in positive_orders} == {"UNPAID","PAID"}
try:
    task.run_repaired_function("import os", [])
    raise AssertionError("unsafe source accepted")
except ValueError: pass
for name in ("b0","b1"): admit(json.loads((task.ROOT/"configs"/(name+".json")).read_text()))
mlp=json.loads((task.ROOT/"configs/b0.json").read_text())
mlp["calibration"]={"kind":"mlp_clip","feature_names":["initial_probability","review_probability","text_length","image_count"],
                    "layers":[{"weight":[[1,0,0,0]],"bias":[0]},{"weight":[[1]],"bias":[0]},{"weight":[[1]],"bias":[0]}]}
admit(mlp); assert calibrate(0.7,mlp["calibration"]) == 0.7
assert calibrate(0.9, {"kind":"affine_clip","a":2,"b":0}) == 1 and calibrate(0.1,{"kind":"affine_clip","a":2,"b":-1}) == 0
bad = json.loads((task.ROOT/"configs/b0.json").read_text()); bad["python_hook"] = "evil"
try:
    admit(bad); raise AssertionError("executable hook accepted")
except ValueError: pass
b = Budget({"calls":3}); assert b.reserve({"calls":1},{"calls":2}); assert not b.reserve({"calls":1},{"calls":2})
try:
    FrozenModelAdapter(); raise AssertionError("backend did not fail closed")
except ModelRuntimeUnavailable: pass
print(json.dumps({"status":"cpu_contracts_passed","splits":summary,"semantic_groups":len(groups),"gpu_or_model_run":False,"official_runtime_validated":False},indent=2))
