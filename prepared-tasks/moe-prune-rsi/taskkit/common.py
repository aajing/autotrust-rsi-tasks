import hashlib
import json
import math
from pathlib import Path

FAMILIES = ("math", "python", "sql", "tool", "visual", "confidence")
SOURCE_REVISION = "7c89590ead085bf77630b4bf68264ea30b6ddc78"

class ContractError(ValueError):
    pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")

def read_json(path):
    return json.loads(Path(path).read_text())

def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(r) + "\n" for r in records))

def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def finite_number(value, name, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ContractError(name + " must be a finite number")
    if low is not None and value < low or high is not None and value > high:
        raise ContractError(name + " out of range")
    return float(value)

def exact_coverage(records, expected_ids, kind):
    ids = [r.get("id") for r in records]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        raise ContractError(kind + " requires exactly one record for every expected ID")
    return {r["id"]: r for r in records}

def paths(root, split):
    if split not in ("practice", "development", "evaluation"):
        raise ContractError("unknown split")
    folder = Path(root) / "data/public"
    return folder / (split + ".inputs.jsonl"), folder / (split + ".gold.jsonl")
