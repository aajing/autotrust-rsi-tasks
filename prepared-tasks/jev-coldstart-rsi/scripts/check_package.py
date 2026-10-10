#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,sha_file,write_json,read_jsonl,split_paths,score_predictions
p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,text=True,capture_output=True)
sys.stdout.write(p.stdout);sys.stderr.write(p.stderr)
q,y=split_paths(ROOT,'dev');ys=read_jsonl(y)
oracle=score_predictions(read_jsonl(q),ys,[{'id':r['id'],'scores':r['ratings']} for r in ys])
pins=json.loads((ROOT/'configs/source-pins.json').read_text())
source_ok=sha_file(ROOT/'data/source/sac_public_2022_06_29.sqlite')==pins['dataset']['sqlite_sha256']
image_manifest=ROOT/'evidence/image-manifest.json'
images_complete=False
if image_manifest.is_file():
    m=json.loads(image_manifest.read_text())
    files=m.get('files',[])
    expected={(r['split'],r['asset']) for r in read_jsonl(ROOT/'data/public/image-requests.jsonl')}
    actual={(r['split'],r['asset']) for r in files}
    images_complete=m.get('status')=='complete' and len(files)==len(actual)==len(expected)==3560 and actual==expected
    if images_complete:
        for r in files:
            path=ROOT/'data'/'public'/'images'/r['asset']
            if not path.is_file() or sha_file(path)!=r['sha256']:images_complete=False
result={'cpu_contracts_passed':p.returncode==0,'source_metadata_sha256_verified':source_ok,
        'oracle_fixture_score':oracle['score'],'oracle_is_model_result':False,'images_complete':images_complete,
        'gpu_inference_run':False,'official_judge_active':False,'revision_submitted':False}
write_json(ROOT/'evidence/cpu-checks.json',result)
files={str(f.relative_to(ROOT)):sha_file(f) for f in sorted(ROOT.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name!='manifest.json'}
write_json(ROOT/'manifest.json',{'kind':'public_proposal_package','evaluation_answers_public':True,'encrypted':False,'files':files})
print(json.dumps(result,indent=2));sys.exit(0 if p.returncode==0 and source_ok else 1)
