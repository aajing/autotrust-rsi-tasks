#!/usr/bin/env python3
"""Read the existing official tar safely and copy only the 3,560 selected images."""
import argparse,io,json,sys,tarfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,read_jsonl,write_json,sha_file
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);a=p.parse_args()
wanted={r['source_path']:r for r in read_jsonl(ROOT/'data/public/image-requests.jsonl')}
if len(wanted)!=3560:raise SystemExit('Unexpected image request manifest')
found={};pixel_splits={}
with tarfile.open(a.archive,'r|*') as archive:
    for member in archive:
        name=Path(member.name).name
        if name not in wanted:continue
        if not member.isfile() or member.size<=0 or member.size>16*1024*1024:raise ValueError('Invalid selected tar member')
        if name in found:raise ValueError('Duplicate selected member')
        row=wanted[name];f=archive.extractfile(member)
        if f is None:raise ValueError('Unreadable member')
        payload=f.read()
        with Image.open(io.BytesIO(payload)) as image:
            image.verify()
        import hashlib
        h=hashlib.sha256(payload).hexdigest()
        if h in pixel_splits and pixel_splits[h]!=row['split']:raise ValueError('Duplicate image bytes across splits')
        pixel_splits[h]=row['split']
        dest=ROOT/'data'/'public'/'images'/row['asset']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload)
        found[name]={'asset':row['asset'],'split':row['split'],'bytes':len(payload),'sha256':h}
missing=set(wanted)-set(found)
report={'status':'complete' if not missing else 'incomplete','expected':len(wanted),'imported':len(found),
        'missing_source_paths':sorted(missing),'files':sorted(found.values(),key=lambda r:r['asset'])}
write_json(ROOT/'evidence/image-manifest.json',report)
if missing:raise SystemExit(f'{len(missing)} selected images missing; no placeholder substitution allowed')
print(json.dumps({'status':'complete','images':len(found)}))
