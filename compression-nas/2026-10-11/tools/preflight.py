"""Check local proposal handoff structure; this is not an official review."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    "kv-cache-rsi", "vl-activation-quant-rsi", "lowrank-compress-rsi",
    "sparse24-rsi", "jev-block-nas-rsi", "gpt-subnet-nas-rsi",
)
REQUIRED = ("proposal.md", "task.json", "SOURCES.md", "DATA.md", "INTEGRATION.md")


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith(("| Section", "| ---")):
            continue
        cells = re.split(r"(?<!\\)\|", line)[1:-1]
        if len(cells) != 3:
            raise ValueError(f"Expected three table columns: {line[:100]}")
        rows.append(tuple(cell.strip() for cell in cells))
    return rows


def run():
    expected = json.loads((ROOT / "shared/proposal-fields.json").read_text())
    records = []
    for slug in SLUGS:
        folder = ROOT / slug
        problems = []
        for name in REQUIRED:
            if not (folder / name).is_file():
                problems.append(f"Missing {name}")
        record = {"task": slug, "structural_errors": problems}
        if problems:
            records.append(record)
            continue
        body = (folder / "proposal.md").read_text()
        try:
            rows = table_rows(body)
            assert [(r[0], r[1]) for r in rows] == [
                (r["section"], r["field"]) for r in expected
            ], "Official 28-field table/order differs"
            assert all(r[2] for r in rows), "Empty proposal field"
            values = {r[1]: r[2] for r in rows}
            assert "Jing Qiu" in values["Full name"], "Submitting name differs"
            assert "ajing@autotrust.ai" in values["Email"], "Submitting email differs"
            assert re.search(r"\b[0-9a-f]{40}\b", values["Exact commit/tag"]), "Missing immutable source commit"
            assert not re.search(r"[\u4e00-\u9fff]", body), "Proposal is not English-only"
            assert not re.search(r"\b(TODO|TBD|FIXME|PLACEHOLDER)\b", body), "Unresolved placeholder in proposal"
            contract = json.loads((folder / "task.json").read_text(), parse_constant=reject_constant)
            assert isinstance(contract, dict) and contract, "Empty task contract"
            record.update({
                "fields": len(rows), "english_only": True,
                "source_repository": values["Repository URL"],
                "source_revision": values["Exact commit/tag"],
                "proposal_sha256": hashlib.sha256(body.encode()).hexdigest(),
            })
        except (AssertionError, ValueError, KeyError) as error:
            problems.append(str(error))
        records.append(record)
    report = {
        "kind": "local structural preflight, not official approval or GPU validation",
        "tasks": records,
        "passed": all(not r["structural_errors"] for r in records),
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "tasks": [
        {"task": r["task"], "errors": r["structural_errors"]} for r in report["tasks"]
    ]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
