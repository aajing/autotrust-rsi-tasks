#!/usr/bin/env python3
"""Explicit opt-in local-model diagnostic. Never used by prepare/check_package."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,read_jsonl,write_jsonl,split_paths
from src.native_client import LocalJEV
from src.policy import load,rank
p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--split',choices=['train','dev','evaluation'],default='dev');p.add_argument('--output',required=True);p.add_argument('--base-url',default='http://127.0.0.1:8000')
p.add_argument('--policy',default=str(ROOT/'baseline/policy.json'),help='Admitted candidate JSON; default is B0')
a=p.parse_args();out=Path(a.output)
if out.exists():raise SystemExit('Refusing to overwrite predictions')
qs,_=split_paths(ROOT,a.split)
policy=load(a.policy)
client=LocalJEV(a.model_dir,ROOT/'data/public/images',a.base_url,max_calls=20000,seconds=7200)
rows=[]
for q in read_jsonl(qs):rows.append({'id':q['id'],'scores':rank(q,client,policy)})
write_jsonl(out,rows)
print(json.dumps({'status':'complete','diagnostic_only':True,'model_calls':client.calls,'prompt_tokens':client.tokens}))
