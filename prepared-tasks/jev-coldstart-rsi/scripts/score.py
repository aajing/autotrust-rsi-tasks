#!/usr/bin/env python3
"""Diagnostic prediction-file scorer. This is not the trusted official Judge."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,read_jsonl,score_predictions,split_paths
p=argparse.ArgumentParser();p.add_argument('--predictions',required=True);p.add_argument('--split',choices=['train','dev','evaluation'],default='dev')
a=p.parse_args();q,y=split_paths(ROOT,a.split)
try: result=score_predictions(read_jsonl(q),read_jsonl(y),read_jsonl(a.predictions))
except (OSError,ValueError) as e: result={'status':'unscored','score':None,'reason':str(e)}
print(json.dumps(result,indent=2));sys.exit(0 if result['status']=='complete' else 2)
