"""Base-only optional public image fetch. Does not load models or run inference."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--download',action='store_true');args=ap.parse_args()
    manifest=json.loads((ROOT/'data-manifest.json').read_text());rows=json.loads((ROOT/'data/screenspot-selected.json').read_text())
    names={row['img_filename'] for row in rows};out=ROOT/'data/screenspot-images';out.mkdir(exist_ok=True)
    missing=sorted(name for name in names if not (out/name).is_file())
    if not args.download:
        print(json.dumps({'selected_records':len(rows),'unique_images':len(names),'local_images':len(names)-len(missing),'missing_images':len(missing),'download_enabled':False},indent=2));return
    source=manifest['screenspot_images'];cache=ROOT/'.downloads';cache.mkdir(exist_ok=True);archive=cache/'screenspotv2_image.zip'
    if not archive.exists() or archive.stat().st_size!=source['bytes'] or digest(archive)!=source['sha256']:
        partial=archive.with_suffix('.partial')
        with urllib.request.urlopen(source['url'],timeout=120) as response,partial.open('wb') as target:
            while chunk:=response.read(1024*1024):target.write(chunk)
        if partial.stat().st_size!=source['bytes'] or digest(partial)!=source['sha256']:
            raise RuntimeError('Source download incomplete or SHA256 mismatch; no cohort substitution')
        partial.replace(archive)
    with zipfile.ZipFile(archive) as z:
        entries={}
        for info in z.infolist():
            if info.is_dir():continue
            name=Path(info.filename).name
            if name in names:
                if name in entries:raise RuntimeError('Duplicate selected basename in archive: '+name)
                entries[name]=info
        if set(entries)!=names:raise RuntimeError('Missing selected images in pinned archive')
        hashes={}
        for name in sorted(names):
            if Path(name).name!=name:raise RuntimeError('Unsafe selected filename')
            data=z.read(entries[name]);(out/name).write_bytes(data);hashes[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    (ROOT/'data/screenspot-image-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps({'verified_archive_sha256':source['sha256'],'extracted_images':len(hashes),'records':len(rows)},indent=2))

if __name__=='__main__':main()
