#!/usr/bin/env python3
"""Export the complete public research package; no answer or seed is withheld."""
import argparse,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,read_jsonl,sha_file,write_json
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--metadata-only',action='store_true');a=p.parse_args()
out=Path(a.output).resolve()
if out.exists():raise SystemExit('Refusing to overwrite output')
images={Path(r['image']).name for s in ('train','dev','evaluation') for q in read_jsonl(ROOT/f'data/public/{s}.jsonl') for r in q['history']+q['candidates'] if 'image' in r}
missing=[x for x in images if not (ROOT/'data/public/images'/x).is_file()]
if missing and not a.metadata_only:raise SystemExit(f'{len(missing)} Work images missing; use --metadata-only for an explicitly incomplete review bundle')
files=[]
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.is_symlink() or any(x in path.parts for x in ('__pycache__','.git','.venv')):continue
    if path.suffix in ('.pyc','.pyo') or path.name=='.DS_Store':continue
    if a.metadata_only and 'images' in path.relative_to(ROOT).parts:continue
    files.append(path.relative_to(ROOT).as_posix())
for rel in files:
    dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
write_json(out/'WORK-MANIFEST.json',{'image_assets_complete':not missing and not a.metadata_only,
                                  'official_runtime_active':False,'metadata_only':a.metadata_only,
                                  'evaluation_answers_public':True,'source_metadata_public':True,'encrypted':False,
                                  'files':{f:sha_file(out/f) for f in files}})
print(out)
