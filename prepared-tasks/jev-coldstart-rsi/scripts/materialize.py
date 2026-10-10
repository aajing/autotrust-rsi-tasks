#!/usr/bin/env python3
"""Materialize B0 policy files only. No inference, training or network access."""
import argparse,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(a.output).resolve()
if out.exists(): raise SystemExit('Refusing to overwrite an existing path')
out.mkdir(parents=True)
for name in ('policy.json','policy.py'): shutil.copy2(root/'baseline'/name,out/name)
print(out)
