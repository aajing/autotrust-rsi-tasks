#!/usr/bin/env python3
"""Explicit construction command; never invoked by CPU checks or Solution."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);args=p.parse_args()
from huggingface_hub import snapshot_download
manifest=json.loads((ROOT/"configs/source_manifest.json").read_text())
for source in manifest["sources"]:
    target=args.output/source["repo"].split("/")[-1]
    snapshot_download(repo_id=source["repo"],revision=source["revision"],
                      allow_patterns=[f["path"] for f in source["files"]],local_dir=target)
    for info in source["files"]:
        path=target/info["path"]
        if info["bytes"] is not None and path.stat().st_size!=info["bytes"]: raise ValueError("size mismatch: "+str(path))
        if info["lfs_sha256"]:
            digest=hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b""):digest.update(block)
            if digest.hexdigest()!=info["lfs_sha256"]:raise ValueError("LFS hash mismatch: "+str(path))
print("Pinned snapshot downloads and listed LFS hashes verified; no model started.")
