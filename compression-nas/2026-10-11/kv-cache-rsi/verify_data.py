"""Validate frozen public inputs without loading any remote code or model."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
m=json.loads((R/'data-manifest.json').read_text());total=0
for family,meta in m['families'].items():
 p=R/'data'/f'{family}.jsonl';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['selected_file_sha256'];rows=[json.loads(x) for x in raw.splitlines()];assert len(rows)==meta['selected_rows']==32;assert [x['_id'] for x in rows]==meta['ids'];assert len(set(meta['ids']))==32
 assert rows==sorted(rows,key=lambda x:hashlib.sha256((family+'\0'+x['_id']).encode()).hexdigest());assert all(x['answers'] and x['context'] for x in rows);total+=len(rows)
assert total==192
print(json.dumps({'status':'pass','families':len(m['families']),'selected_records':total,'sha256_verified_files':6,'gpu_used':False},indent=2))
