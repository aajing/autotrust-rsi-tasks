"""Validate local annotations and bundled images; never silently fetch data."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
m=json.loads((R/'data-manifest.json').read_text());chart=json.loads((R/'data/chartqa-selected.json').read_text());screen=json.loads((R/'data/screenspot-selected.json').read_text());rows=chart+screen
assert len(rows)==len(m['records'])==320
assert len({x['record_id'] for x in rows})==320
for family,count in m['source_counts'].items():
 selected=[x for x in rows if x['family']==family];assert len(selected)==64
 if family.startswith('chartqa_'):source=json.loads((R/f'evidence/chartqa-test-{family.removeprefix("chartqa_")}.json').read_text())
 else:source=json.loads((R/f'evidence/{family}_v2.json').read_text())
 assert len(source)==count
 expected=sorted(range(count),key=lambda i:hashlib.sha256((family+'\0'+str(i)).encode()).hexdigest())[:64];assert [x['source_index'] for x in selected]==expected
 for x in selected:
  original=source[x['source_index']]
  assert all(x[k]==value for k,value in original.items())
hashes=json.loads((R/'data/chartqa-image-hashes.json').read_text());assert len(hashes)==124
for name,item in hashes.items():
 raw=(R/'data/chartqa-images'/name).read_bytes();assert len(raw)==item['bytes'];assert hashlib.sha256(raw).hexdigest()==item['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob_sha1']
print(json.dumps({'status':'pass','selected_records':320,'source_counts_verified':m['source_counts'],'bundled_chartqa_images_verified':124,'screenspot_archive_downloaded':False,'gpu_used':False},indent=2))
