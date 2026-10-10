#!/usr/bin/env python3
"""Build complete public unencrypted bundles. No network or official submission."""
import argparse,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TASKS=('gev-think-rsi','jev-judge-rsi','jev-coldstart-rsi','jev-visual-control-rsi','gev-quant-rsi','moe-prune-rsi')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def allowed(path):
    return path.is_file() and not path.is_symlink() and not any(p in {'.git','__pycache__','.pytest_cache','.venv','.DS_Store'} for p in path.parts) and path.suffix not in {'.pyc','.pyo'}

def build(destination):
    destination.mkdir(parents=True,exist_ok=True);records=[]
    for name in TASKS:
        task=ROOT/name
        if not (task/'proposal.md').is_file():raise ValueError('Missing proposal: '+name)
        files=sorted(f for f in task.rglob('*') if allowed(f))
        target=destination/(name+'-public.zip')
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for f in files:
                rel=Path(name)/f.relative_to(task);info=zipfile.ZipInfo(rel.as_posix(),date_time=(2026,10,10,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,f.read_bytes())
        with zipfile.ZipFile(target) as z:
            bad=z.testzip()
            if bad:raise ValueError('Corrupt ZIP member: '+bad)
            if any(i.flag_bits&1 for i in z.infolist()):raise ValueError('Unexpected encryption')
            if any(Path(i.filename).is_absolute() or '..' in Path(i.filename).parts for i in z.infolist()):raise ValueError('Unsafe archive path')
        records.append({'task':name,'file':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'files':len(files),
                        'encrypted':False,'kind':'public_proposal_package','evaluation_answers_public':True,
                        'all_prepared_task_assets_included':True})
    (destination/'SHA256SUMS').write_text(''.join(f"{r['sha256']}  {r['file']}\n" for r in records))
    combined=destination/'autotrust-six-task-proposals-public.zip'
    draft=ROOT.parent/'draft-proposals/2026-10-10'
    common=[ROOT/n for n in ('README.md','STATUS.md','build_archives.py','review_documents.py')]
    all_files=common+[f for name in TASKS for f in (ROOT/name).rglob('*') if allowed(f)]+[f for f in draft.rglob('*') if allowed(f)]
    with zipfile.ZipFile(combined,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(all_files):
            rel=Path('autotrust-rsi-prepared')/f.relative_to(ROOT.parent)
            info=zipfile.ZipInfo(rel.as_posix(),date_time=(2026,10,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,f.read_bytes())
    with zipfile.ZipFile(combined) as z:
        if z.testzip() or any(i.flag_bits&1 for i in z.infolist()):raise ValueError('Invalid combined archive')
    bundle={'file':combined.name,'bytes':combined.stat().st_size,'sha256':sha(combined),'files':len(all_files),
            'encrypted':False,'kind':'public_proposal_package','evaluation_answers_public':True,'all_prepared_task_assets_included':True}
    with (destination/'SHA256SUMS').open('a') as f:f.write(f"{bundle['sha256']}  {bundle['file']}\n")
    (destination/'archives.json').write_text(json.dumps({'official_submission_status':'not submitted to official review','archives':records,'combined_bundle':bundle},indent=2)+'\n')
    records.append(bundle)
    return records

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'dist'));a=p.parse_args()
    print(json.dumps(build(Path(a.output).resolve()),indent=2))
