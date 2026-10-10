#!/usr/bin/env python3
"""Fetch pinned small source metadata, or explicitly opt in to the 86.6 GB archive."""
import argparse,json,sys,urllib.request,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,sha_file
p=argparse.ArgumentParser();p.add_argument('--images',action='store_true',help='Download full 86,569,533,440-byte source archive; not needed for metadata preparation')
a=p.parse_args();pins=json.loads((ROOT/'configs/source-pins.json').read_text())['dataset']
if a.images:
    target=ROOT/'data/source/sac.tar';url=pins['image_archive_url'];size=pins['image_archive_bytes']
else:
    target=ROOT/'data/source/sac_public_2022_06_29.sqlite';url=pins['sqlite_url'];size=pins['sqlite_bytes']
if target.exists():
    if target.stat().st_size!=size:raise SystemExit('Existing payload has unexpected size')
    if not a.images and sha_file(target)!=pins['sqlite_sha256']:raise SystemExit('SQLite checksum mismatch')
    print('Existing source verified' if not a.images else 'Existing archive size checked; import records selected image hashes');sys.exit(0)
target.parent.mkdir(parents=True,exist_ok=True);part=target.with_suffix(target.suffix+'.part')
with urllib.request.urlopen(url,timeout=90) as src,part.open('wb') as out:
    if a.images and src.headers.get('ETag','').strip('"')!=pins['image_archive_etag']:raise SystemExit('Archive ETag changed; review before importing')
    shutil.copyfileobj(src,out,length=1<<20)
if part.stat().st_size!=size:raise SystemExit('Incomplete source download; .part retained for inspection')
if not a.images and sha_file(part)!=pins['sqlite_sha256']:raise SystemExit('Source checksum mismatch')
part.rename(target);print(target)
