"""Build ordinary unencrypted review archives from completed local proposals."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from preflight import ROOT, SLUGS, run


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_files():
    return sorted(
        p for p in ROOT.rglob("*") if p.is_file()
        and not any(part in {"dist", ".cache", "__pycache__", ".pytest_cache", ".git"}
                    for part in p.relative_to(ROOT).parts)
        and p.suffix not in {".pyc", ".pyo"}
        and p.name != "MANIFEST.files.json"
    )


def archive(path, files):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for source in sorted(files):
            rel = source.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with source.open("rb") as stream, out.open(info, "w", force_zip64=True) as target:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    target.write(block)
    with zipfile.ZipFile(path) as check:
        assert check.testzip() is None, f"Corrupt archive: {path}"
        assert all(not (entry.flag_bits & 1) for entry in check.infolist()), "Encrypted entry"
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": digest(path), "encrypted": False}


def main():
    preflight = run()
    if not preflight["passed"]:
        raise SystemExit("Complete the six proposal packages and pass preflight first.")
    files = source_files()
    manifest = {
        "scope": "local review handoff, not official submission",
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                   "sha256": digest(p)} for p in files],
    }
    manifest_path = ROOT / "MANIFEST.files.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    files.append(manifest_path)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    results = []
    for slug in SLUGS:
        selected = [p for p in files if p.relative_to(ROOT).parts[0] in {slug, "shared"}]
        results.append(archive(dist / f"{slug}-proposal.zip", selected))
    results.append(archive(dist / "compression-nas-six-proposals.zip", files))
    (dist / "archives.json").write_text(json.dumps({"archives": results}, indent=2) + "\n")
    (dist / "SHA256SUMS").write_text("".join(f"{r['sha256']}  {r['file']}\n" for r in results))
    print(json.dumps({"archives": results, "integrity_checked": True, "encrypted": False}, indent=2))


if __name__ == "__main__":
    main()
