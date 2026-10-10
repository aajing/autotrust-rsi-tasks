"""Materialize existing pinned B0 from the standard Hugging Face snapshot cache.

No model load, training, profiling, pruning, quantization, evaluation or network.
Author setup first runs the pinned `hf download` command in RUNBOOK.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
REVISION = "7c89590ead085bf77630b4bf68264ea30b6ddc78"
REPO_ID = "autotrust/GEV-26B-Decide"


def hash_file(path, algorithm="sha256", git_blob=False):
    digest = hashlib.new(algorithm)
    if git_blob:
        digest.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_snapshot(source, inventory=None):
    source = Path(source).absolute()
    if not source.is_dir():
        raise ValueError("Pinned upstream snapshot is absent. Run the exact hf download command in RUNBOOK.md during author setup.")
    if source.name != REVISION or source.parent.name != "snapshots":
        raise ValueError("Use the standard Hugging Face cache snapshots/<pinned revision> directory, not an unbound local export.")
    blobs = (source.parent.parent / "blobs").resolve()
    paths = sorted(p for p in source.rglob("*") if p.is_file() or p.is_symlink())
    files = {}
    expected = None
    if inventory is not None:
        expected = json.loads(Path(inventory).read_text())
        if expected.get("schema") != "upstream-blob-inventory-v1" or expected.get("repo_id") != REPO_ID or expected.get("revision") != REVISION or not expected.get("files"):
            raise ValueError("Upstream inventory identity mismatch.")
        expected = expected["files"]
        if set(expected) != {path.relative_to(source).as_posix() for path in paths}:
            raise ValueError("Snapshot/upstream inventory coverage mismatch.")
    for path in paths:
        target = path.resolve()
        if not path.is_symlink() or target.parent != blobs or not target.is_file():
            raise ValueError("Snapshot files must resolve to this repository's verified Hugging Face blob cache.")
        name = target.name
        if expected is not None:
            record = expected[path.relative_to(source).as_posix()]
            if record.get("content_address") != name or record.get("bytes") != target.stat().st_size:
                raise ValueError("Snapshot file is not the exact upstream revision member.")
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", name):
            raise ValueError("Unexpected cached blob identifier.")
        actual = hash_file(target, "sha1" if len(name) == 40 else "sha256", git_blob=len(name) == 40)
        if actual != name:
            raise ValueError("Cached upstream blob content hash mismatch.")
        files[path.relative_to(source).as_posix()] = hash_file(target)
    required = {"config.json", "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json", "processor_config.json", "chat_template.jinja", "head.safetensors", "calibration.json", "calibration_gold.json", "judge_config.json"}
    if not required <= files.keys():
        raise ValueError("Pinned snapshot is incomplete: " + ", ".join(sorted(required - files.keys())))
    receipts = json.loads((ROOT / "source/metadata-receipts.json").read_text())
    for filename in ("config.json", "model.safetensors.index.json"):
        if files[filename] != receipts["files"][filename]["sha256"]:
            raise ValueError("Pinned source config/index mismatch.")
    index = json.loads((source / "model.safetensors.index.json").read_text())
    shards = set(index["weight_map"].values())
    if not shards <= files.keys():
        raise ValueError("Pinned model shards are missing.")
    if not any(name.startswith("adapter/") and name.endswith(".safetensors") for name in files):
        raise ValueError("Original System 1 adapter is missing.")
    # Header reads only: confirm every indexed tensor has a real, correctly sized
    # safetensors payload. Never deserialize tensors or execute repository code.
    seen = {}
    payload_bytes = 0
    for name in sorted(shards):
        path = source / name
        with path.open("rb") as stream:
            size = int.from_bytes(stream.read(8), "little")
            if not 2 <= size <= 16 * 1024 * 1024:
                raise ValueError("Invalid safetensors header.")
            header = json.loads(stream.read(size))
        payload_size = path.stat().st_size - 8 - size
        intervals = []
        for tensor, details in header.items():
            if tensor == "__metadata__":
                continue
            offsets = details.get("data_offsets")
            if not isinstance(offsets, list) or len(offsets) != 2 or not all(type(v) is int for v in offsets) or not 0 <= offsets[0] <= offsets[1] <= payload_size:
                raise ValueError("Invalid tensor payload range.")
            if tensor in seen or index["weight_map"].get(tensor) != name:
                raise ValueError("Safetensors/index mapping mismatch.")
            seen[tensor] = name
            intervals.append(tuple(offsets))
            payload_bytes += offsets[1] - offsets[0]
        intervals.sort()
        if not intervals or intervals[0][0] != 0 or intervals[-1][1] != payload_size or any(a[1] != b[0] for a, b in zip(intervals, intervals[1:])):
            raise ValueError("Safetensors payload is incomplete or overlapping.")
    if seen != index["weight_map"] or payload_bytes != index["metadata"]["total_size"]:
        raise ValueError("Complete pinned backbone inventory mismatch.")
    return source, files


def materialize(source, output, inventory=None):
    source, files = inspect_snapshot(source, inventory)
    output = Path(output).absolute()
    if output.exists() or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError("Output must be a new independent directory.")
    output.mkdir(parents=True)
    for name in files:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
        if hash_file(target) != files[name]:
            raise ValueError("Copied B0 content hash mismatch; incomplete output must not be evaluated.")
    receipt = {"schema": "prepared-upstream-baseline-v1", "status": "materialized", "baseline_id": "B0", "artifact_kind": "original_bf16", "repo_id": REPO_ID, "revision": REVISION, "files": files, "model_computation_performed": False, "measurements_available": False, "upstream_inventory_verified": inventory is not None}
    (output / "prepared-artifact.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--inventory", help="Optional exact-revision upstream blob inventory fetched during author setup")
    args = parser.parse_args()
    try:
        print(materialize(args.source_snapshot, args.output, args.inventory))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
