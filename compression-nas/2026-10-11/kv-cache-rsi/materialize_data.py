"""Fetch the pinned public LongBench archive and reproduce the fixed plaintext cohort.

Standard library only. Network access is setup-only; Work/Judge remain offline.
No archive code is executed and ZIP paths are never extracted to the filesystem.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE_URL = "https://huggingface.co/datasets/zai-org/LongBench/resolve/5e628be450b7e67fb7ae6e201bd6d8f7056f7672/data.zip"
ARCHIVE_SHA256 = "cb45b11a4133c6bc1d6a44b0f8e701335ff1e543195db1103472e575857f7f64"
ARCHIVE_BYTES = 113932529
FAMILIES = ("qasper", "hotpotqa", "musique", "gov_report", "passage_count", "passage_retrieval_en")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_archive(path):
    require(path.stat().st_size == ARCHIVE_BYTES, "archive byte count mismatch")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    require(digest.hexdigest() == ARCHIVE_SHA256, "archive SHA256 mismatch")


def fetch_archive(cache):
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / (ARCHIVE_SHA256 + ".zip")
    if target.exists():
        verify_archive(target)
        return target
    descriptor, temporary = tempfile.mkstemp(prefix="longbench-", suffix=".part", dir=cache)
    temporary = Path(temporary)
    try:
        digest, size = hashlib.sha256(), 0
        request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "OpenRSI-data-materializer/1.0"})
        with os.fdopen(descriptor, "wb") as destination, urllib.request.urlopen(request, timeout=60) as source:
            require(source.geturl().startswith("https://"), "non-HTTPS download redirect")
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                require(size <= ARCHIVE_BYTES, "download exceeds pinned byte count")
                digest.update(block)
                destination.write(block)
            destination.flush()
            os.fsync(destination.fileno())
        require(size == ARCHIVE_BYTES, "incomplete archive download")
        require(digest.hexdigest() == ARCHIVE_SHA256, "download SHA256 mismatch")
        os.replace(temporary, target)
        return target
    finally:
        temporary.unlink(missing_ok=True)


def select_payload(family, source_bytes, entry):
    require(hashlib.sha256(source_bytes).hexdigest() == entry["source_sha256"], "source member SHA256 mismatch: " + family)
    rows = [json.loads(line) for line in source_bytes.decode("utf-8").splitlines()]
    require(len(rows) == entry["source_rows"] == 200, "source cardinality mismatch: " + family)
    require(all(isinstance(row, dict) and isinstance(row.get("_id"), str) and row.get("dataset") == family for row in rows), "invalid source record: " + family)
    require(len({row["_id"] for row in rows}) == len(rows), "duplicate source IDs: " + family)
    rows.sort(key=lambda row: hashlib.sha256((family + "\0" + row["_id"]).encode("utf-8")).hexdigest())
    require(entry["selected_rows"] == len(entry["ids"]) == 32, "selection cardinality mismatch: " + family)
    selected = rows[:32]
    require([row["_id"] for row in selected] == entry["ids"], "selection order mismatch: " + family)
    payload = ("\n".join(json.dumps(row, ensure_ascii=False) for row in selected) + "\n").encode("utf-8")
    require(hashlib.sha256(payload).hexdigest() == entry["selected_file_sha256"], "selected file SHA256 mismatch: " + family)
    return payload


def validate_cohort(archive, manifest):
    require(manifest["archive_url"] == ARCHIVE_URL and manifest["archive_sha256"] == ARCHIVE_SHA256 and manifest["archive_bytes"] == ARCHIVE_BYTES, "manifest archive pin mismatch")
    require(set(manifest["families"]) == set(FAMILIES) and manifest["total_selected"] == 192, "manifest family/count mismatch")
    verify_archive(archive)
    payloads = {}
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        for family in FAMILIES:
            entry = manifest["families"][family]
            member = "data/" + family + ".jsonl"
            require(entry["source_entry"] == member and names.count(member) == 1, "missing, duplicate or unexpected ZIP member: " + family)
            payloads[family] = select_payload(family, zipped.read(member), entry)
    return payloads


def write_cohort(payloads, output):
    # All six files have already passed validation before any output is changed.
    output.mkdir(parents=True, exist_ok=True)
    for family, payload in payloads.items():
        target = output / (family + ".jsonl")
        if target.exists() and target.read_bytes() == payload:
            continue
        descriptor, temporary = tempfile.mkstemp(prefix=family + "-", suffix=".part", dir=output)
        temporary = Path(temporary)
        try:
            with os.fdopen(descriptor, "wb") as destination:
                destination.write(payload)
                destination.flush()
                os.fsync(destination.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="existing pinned ZIP; do not use network")
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "longbench", help="verified download cache directory")
    parser.add_argument("--output", type=Path, default=ROOT / "data", help="plaintext selected-data directory")
    parser.add_argument("--verify-only", action="store_true", help="validate source and reconstructed bytes without writing selected data")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "data-manifest.json").read_text(encoding="utf-8"))
    archive = args.archive if args.archive is not None else fetch_archive(args.cache)
    payloads = validate_cohort(archive, manifest)
    if not args.verify_only:
        write_cohort(payloads, args.output)
    print(json.dumps({"status": "verified", "families": len(payloads), "records": 192, "archive_sha256": ARCHIVE_SHA256, "selected_files_sha256": {family: hashlib.sha256(payload).hexdigest() for family, payload in payloads.items()}, "data_written": not args.verify_only}, indent=2))


if __name__ == "__main__":
    main()
