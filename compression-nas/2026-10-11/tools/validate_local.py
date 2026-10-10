"""Run local CPU contracts and verify the included data; no models or network."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from preflight import ROOT, SLUGS, reject_constant, run


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = {"scope": "local CPU and file checks only; not GPU results or official approval",
              "structural_preflight": run(), "suites": [], "file_checks": []}
    for slug in SLUGS:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "-v", "test_scoring.py"],
            cwd=ROOT / slug, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        match = re.search(r"Ran (\d+) tests?", output)
        report["suites"].append({"task": slug, "passed": result.returncode == 0,
                                 "tests": int(match[1]) if match else 0,
                                 "output": output})
    def check(label, condition):
        report["file_checks"].append({"check": label, "passed": bool(condition)})

    kv = ROOT / "kv-cache-rsi"
    manifest = json.loads((kv / "data-manifest.json").read_text())
    for family, record in manifest["families"].items():
        path = kv / "data" / (family + ".jsonl")
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        check("LongBench hash/count/IDs: " + family,
              sha256(path) == record["selected_file_sha256"]
              and len(rows) == record["selected_rows"] == 32
              and [row["_id"] for row in rows] == record["ids"])

    vl = ROOT / "vl-activation-quant-rsi"
    manifest = json.loads((vl / "data/chartqa-image-hashes.json").read_text())
    for name, record in manifest.items():
        path = vl / "data/chartqa-images" / name
        check("ChartQA image: " + name,
              sha256(path) == record["sha256"] and path.stat().st_size == record["bytes"])

    for slug in ("lowrank-compress-rsi", "sparse24-rsi"):
        folder = ROOT / slug / "data"
        manifest = json.loads((folder / "manifest.json").read_text())
        for name, expected in manifest["files"].items():
            check(slug + " data: " + name, sha256(folder / name) == expected)

    json_count = 0
    syntax_count = 0
    for slug in SLUGS:
        for path in (ROOT / slug).rglob("*.json"):
            json.loads(path.read_text(), parse_constant=reject_constant)
            json_count += 1
        for path in (ROOT / slug).glob("*.py"):
            ast.parse(path.read_text(), filename=str(path))
            syntax_count += 1
    report["json_files_parsed"] = json_count
    report["task_python_files_parsed"] = syntax_count
    report["test_count"] = sum(suite["tests"] for suite in report["suites"])
    report["passed"] = (report["structural_preflight"]["passed"]
                        and all(suite["passed"] for suite in report["suites"])
                        and all(item["passed"] for item in report["file_checks"]))
    (ROOT / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "test_count": report["test_count"],
                      "file_checks": len(report["file_checks"]),
                      "json_files_parsed": json_count,
                      "task_python_files_parsed": syntax_count}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
