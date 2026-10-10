"""Fetch exact-revision upstream file metadata only; never download model weights."""
import argparse
import json
from pathlib import Path
import urllib.request

REVISION = "7c89590ead085bf77630b4bf68264ea30b6ddc78"
REPO_ID = "autotrust/GEV-26B-Decide"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    url = f"https://huggingface.co/api/models/{REPO_ID}/revision/{REVISION}?blobs=true"
    with urllib.request.urlopen(url, timeout=30) as response:
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000:
        raise SystemExit("Unexpectedly large metadata response.")
    metadata = json.loads(raw)
    if metadata.get("sha") != REVISION or not metadata.get("siblings"):
        raise SystemExit("Upstream revision or inventory mismatch.")
    files = {}
    for item in metadata["siblings"]:
        name = item["rfilename"]
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or name in files:
            raise SystemExit("Invalid inventory path.")
        lfs = item.get("lfs") or {}
        expected = lfs.get("sha256") or item.get("blobId")
        if not expected or len(expected) not in (40, 64) or type(item.get("size")) is not int:
            raise SystemExit("Missing exact blob metadata; no partial inventory written.")
        files[name] = {"content_address": expected, "algorithm": "sha256" if lfs else "git-blob-sha1", "bytes": item["size"]}
    result = {"schema": "upstream-blob-inventory-v1", "repo_id": REPO_ID, "revision": REVISION, "source_url": url, "files": files, "model_weights_downloaded": False}
    destination = Path(args.output)
    if destination.exists():
        raise SystemExit("Output already exists; select a new path to preserve evidence.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Saved metadata for {len(files)} files; no weights downloaded.")


if __name__ == "__main__":
    main()
