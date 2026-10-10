"""Fetch pinned small metadata only. Never downloads model weights or tokenizer payloads."""
import argparse
import json
from pathlib import Path
import sys
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from taskkit.common import SOURCE_REVISION,file_hash,write_json
from taskkit.tensors import select_expert_tensors

p=argparse.ArgumentParser();p.add_argument("--proxy");args=p.parse_args()
root=Path(__file__).resolve().parents[1];folder=root/"source/metadata";folder.mkdir(parents=True,exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({"https":args.proxy})) if args.proxy else urllib.request.build_opener()
receipts={}
for filename in ("config.json","model.safetensors.index.json"):
    url=f"https://huggingface.co/autotrust/GEV-26B-Decide/raw/{SOURCE_REVISION}/{filename}"
    for attempt in range(3):
        try:
            raw=opener.open(url,timeout=30).read(2_000_001)
            break
        except OSError:
            if attempt==2:raise
    if len(raw)>2_000_000:raise SystemExit("Unexpected metadata size.")
    json.loads(raw);dest=folder/filename;dest.write_bytes(raw)
    receipts[filename]={"url":url,"sha256":file_hash(dest),"bytes":len(raw)}
index=json.loads((folder/"model.safetensors.index.json").read_text())
write_json(root/"source/metadata-receipts.json",{"files":receipts,"source_revision":SOURCE_REVISION,"expert_tensors":select_expert_tensors(index["weight_map"])})
print("Pinned metadata saved; no weights were downloaded.")
