"""CPU authoring and diagnostic scoring; no model results are manufactured here."""
from __future__ import annotations
import hashlib, json, math, sqlite3, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ('text', 'image', 'both')
COUNTS = {'train': 57, 'dev': 16, 'evaluation': 16}

def digest(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def read_jsonl(path):
    with Path(path).open() as f: return [json.loads(line) for line in f if line.strip()]

def write_jsonl(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rows))

def split_for(sid):
    n = int(digest('sac-coldstart-v1:'+str(sid)), 16) % 10
    return 'train' if n < 6 else 'dev' if n < 8 else 'evaluation'

def build(root=ROOT):
    """Frozen metadata split. Source identity maps and all answer files are openly released."""
    root = Path(root)
    source = root/'data/source/sac_public_2022_06_29.sqlite'
    pins = json.loads((root/'configs/source-pins.json').read_text())
    if sha_file(source) != pins['dataset']['sqlite_sha256']:
        raise ValueError('Source SQLite checksum mismatch')
    con = sqlite3.connect('file:'+str(source)+'?mode=ro', uri=True)
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('Invalid SQLite')
    valid_users = set()
    survey = defaultdict(list)
    for sid, qid, rating in con.execute('SELECT id,qid,rating FROM survey'):
        survey[sid].append((qid,rating))
    for sid, rows in survey.items():
        if len(rows)==20 and {q for q,r in rows}==set(range(20)) and all(1<=r<=10 for q,r in rows):
            valid_users.add(sid)
    # Do not privilege the small "verified" subset: retain all valid explicit ratings.
    grouped = defaultdict(lambda: defaultdict(list))
    for sid,iid,rating,gid,prompt,path in con.execute('''SELECT r.sid,r.iid,r.rating,i.gid,g.prompt,p.path
        FROM ratings r JOIN images i ON i.id=r.iid JOIN generations g ON g.id=i.gid JOIN paths p ON p.iid=i.id'''):
        if sid not in valid_users or not 1<=rating<=10 or not isinstance(prompt,str) or not prompt.strip(): continue
        if Path(path).name != path or Path(path).suffix.lower() != '.png': continue
        normalized = ' '.join(prompt.casefold().split())
        grouped[sid][normalized].append(dict(iid=iid,gid=gid,prompt=prompt,source_path=path,rating=rating))
    con.close()
    # A normalized prompt belongs to exactly one user's group for this task. This
    # conservative global de-duplication prevents paraphernalia shared across splits.
    owners = defaultdict(set)
    for sid, groups in grouped.items():
        for prompt in groups: owners[prompt].add(sid)
    eligible = defaultdict(list)
    user_items = {}
    for sid, groups in grouped.items():
        items=[]
        for prompt, rows in groups.items():
            if len(owners[prompt])!=1: continue
            item = min(rows, key=lambda r: digest(f"sac-image-v1:{sid}:{r['iid']}"))
            item = dict(item, prompt_hash=digest(prompt))
            items.append(item)
        if len(items)>=40:
            user_items[sid]=items; eligible[split_for(sid)].append(sid)
    source_map=[]; image_requests={}; all_gold={}; counts={}; collisions={}
    for split,n in COUNTS.items():
        if len(eligible[split]) != n:
            raise ValueError(f'{split}: expected all {n} pinned-source eligible users, found {len(eligible[split])}; no silent filtering')
        selected = sorted(eligible[split],key=lambda sid:digest(f'sac-select-v1:{split}:{sid}'))[:n]
        queries=[]; gold=[]; split_prompt_hashes=set()
        for sid in selected:
            records=sorted(user_items[sid],key=lambda r:digest(f"sac-partition-v1:{sid}:{r['iid']}"))[:40]
            history, candidates=records[:20],records[20:]
            # Order is frozen random presentation order, NOT a claimed chronology.
            candidates=sorted(candidates,key=lambda r:digest(f"sac-candidate-order-v1:{sid}:{r['iid']}"))
            user_group=digest(f'sac-user-v1:{split}:{sid}')[:20]
            source_map.append({'split':split,'user_group':user_group,'source_sid':sid,
                                'history_iids':[r['iid'] for r in history],'candidate_iids':[r['iid'] for r in candidates]})
            for r in records:
                asset=digest('sac-asset-v1:'+str(r['iid']))+'.png'
                entry={'asset':asset,'source_path':r['source_path'],'source_iid':r['iid'],'split':split}
                if asset in image_requests and image_requests[asset]['split'] != split: raise ValueError('Image split leak')
                image_requests[asset]=entry; split_prompt_hashes.add(r['prompt_hash'])
            for mode in MODES:
                for length in (3,20):
                    cell=f'{mode}-{length}'; qid=digest(f'sac-query-v1:{split}:{sid}:{cell}')[:24]
                    def visible(r,handle,is_history=False):
                        result={'handle':handle}
                        if mode in ('text','both'): result['text']=r['prompt']
                        if mode in ('image','both'): result['image']='images/'+digest('sac-asset-v1:'+str(r['iid']))+'.png'
                        if is_history: result['rating']=r['rating']
                        return result
                    hs=[visible(r,f'h{i}',True) for i,r in enumerate(history[:length])]
                    cs=[visible(r,f'c{i}') for i,r in enumerate(candidates)]
                    queries.append({'id':qid,'cell':cell,'user_group':user_group,'history':hs,'candidates':cs})
                    gold.append({'id':qid,'cell':cell,'user_group':user_group,
                                 'ratings':{f'c{i}':r['rating'] for i,r in enumerate(candidates)}})
        collisions[split]=split_prompt_hashes
        dest=root/'data'/'public'
        write_jsonl(dest/f'{split}.jsonl',queries); write_jsonl(dest/f'{split}-labels.jsonl',gold)
        all_gold[split]=gold; counts[split]={'users':len(selected),'queries':len(queries),'cells':6,'candidates_per_query':20}
    if any(collisions[a]&collisions[b] for a,b in [('train','dev'),('train','evaluation'),('dev','evaluation')]):
        raise ValueError('Normalized prompt leakage across splits')
    write_jsonl(root/'data/public/source-map.jsonl',source_map)
    write_jsonl(root/'data/public/image-requests.jsonl',sorted(image_requests.values(),key=lambda r:r['asset']))
    report={'source_sqlite_sha256':sha_file(source),'eligible_users_after_filters':{s:len(eligible[s]) for s in COUNTS},
            'selected':counts,'requested_images':len(image_requests),'source_rating_scale':[1,10],
            'history_order':'frozen hash order; no temporal claim','independence_unit':'synthetic survey user ID',
            'public_data_secrecy_claim':False,'image_payload_status':'pending_import',
            'complete_model_evaluation':False,
            'image_byte_duplicates':'retained and reported at import; no pixel-dependent filtering or count change',
            'data_use':'all published inputs and ratings may inform fitting and selection',
            'objective':'benchmark-conditioned ranking; coldstart describes history length, not heldout access'}
    write_json(root/'evidence/split-report.json',report)
    return report

from .metrics import ndcg, score_predictions

def split_paths(root, split):
    d=Path(root)/'data'/'public'
    return d/f'{split}.jsonl',d/f'{split}-labels.jsonl'
