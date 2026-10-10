#!/usr/bin/env python3
"""Diagnostics on any disclosed split; evaluation labels are public."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.metrics import score_predictions

def read(path):
    with Path(path).open() as f:return [json.loads(s) for s in f if s.strip()]

p=argparse.ArgumentParser();p.add_argument('--split',choices=['train','dev','evaluation'],default='dev')
mode=p.add_mutually_exclusive_group(required=True)
mode.add_argument('--predictions',help='CPU-only score of already produced diagnostic outputs')
mode.add_argument('--model-dir',help='Explicitly run B0 against a real local JEV server')
p.add_argument('--output');p.add_argument('--base-url',default='http://127.0.0.1:8000');a=p.parse_args()
qs=read(ROOT/f'data/public/{a.split}.jsonl');ys=read(ROOT/f'data/public/{a.split}-labels.jsonl')
if a.predictions:
    predictions=read(a.predictions)
else:
    if not a.output or Path(a.output).exists():raise SystemExit('Real inference requires a new --output file')
    from src.native_client import LocalJEV
    from baseline.policy import rank
    broker=LocalJEV(a.model_dir,ROOT/'data/public/images',a.base_url,max_calls=20000,seconds=7200)
    predictions=[{'id':q['id'],'scores':rank(q,broker)} for q in qs]
    Path(a.output).write_text(''.join(json.dumps(r)+'\n' for r in predictions))
result=score_predictions(qs,ys,predictions)
print(json.dumps(result,indent=2));sys.exit(0 if result['status']=='complete' else 2)
