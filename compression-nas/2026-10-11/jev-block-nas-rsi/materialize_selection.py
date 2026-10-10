"""Local deterministic source-to-public-evaluation materializer; no network or model."""
import argparse,hashlib,json
from pathlib import Path
SOURCE_SHA='53b044fa5bbcb22164d9a28811e56fabcd82ae29224d994c693b069eeb5d23ed'
def materialize(source:Path,destination:Path):
 digest=hashlib.sha256()
 pools={k:[] for k in ('noul','choice','score')}
 rows=0
 with source.open('rb') as stream:
  for ordinal,line in enumerate(stream):
   digest.update(line)
   if not line.strip():continue
   row=json.loads(line);rows+=1
   if row['source']=='yuri_v3':
    key=hashlib.sha256(('jev-block-nas-rsi:v1:'+row['id']).encode()).hexdigest()
    pools[row['kind']].append((key,ordinal,row))
 if digest.hexdigest()!=SOURCE_SHA or rows!=29955:raise ValueError('Pinned source byte/count mismatch; no fallback dataset')
 selected=[]
 for kind,pool in pools.items():
  if len(pool)<2048:raise ValueError('Insufficient fixed primitive population')
  selected.extend(x[2] for x in sorted(pool,key=lambda x:(x[0],x[1]))[:2048])
 expected=json.loads((Path(__file__).parent/'evaluation-manifest.json').read_text())
 if [x['id'] for x in selected]!=[x['id'] for x in expected]:raise ValueError('Selection differs from public manifest')
 destination.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in selected))
 return len(selected)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(materialize(a.source,a.output))
