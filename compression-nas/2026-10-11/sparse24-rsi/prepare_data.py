"""Build public, deterministic CPU-only research/evaluation assets from pinned data.

Requires pyarrow==25.0.1 and tokenizers==0.22.2; never imports torch or a model.
"""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import re
import shutil
import pyarrow.parquet as pq
from tokenizers import Tokenizer

ROOT=Path(__file__).resolve().parent
SEED="compression-nas-2026-10-10-v1"

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode()).hexdigest()

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")

def jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text("".join(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n" for row in rows))

def number(answer):
    hits=re.findall(r"####\s*([-+]?\d[\d,]*(?:\.\d+)?)",answer)
    if not hits:raise ValueError("Missing gold numeric marker")
    return str(Decimal(hits[-1].replace(",","")).normalize())

def build():
    evidence=ROOT/"evidence";out=ROOT/"data";out.mkdir(exist_ok=True)
    tokenizer=Tokenizer.from_file(str(evidence/"tokenizer.json"))
    wt={};audit={"source_rows":{},"wikitext_tokens":{},"wikitext_distinct_eligible_blocks":{},"gsm8k_distinct_eligible_rows":{}}
    seen=set()
    for original,role,count in [('test','evaluation',128),('validation','development',64),('train','practice',256)]:
        rows=pq.read_table(evidence/f'wikitext-{original}.parquet').to_pylist();audit['source_rows'][f'wikitext/{original}']=len(rows)
        text='\n\n'.join(row['text'] for row in rows)
        tokens=tokenizer.encode(text,add_special_tokens=False).ids;audit['wikitext_tokens'][original]=len(tokens)
        candidates=[]
        for start in range(0,len(tokens)-511,512):
            chunk=tokens[start:start+512];h=digest(chunk)
            if h in seen:continue
            seen.add(h);candidates.append({'id':'wiki-'+h[:20],'source_split':original,'start_token':start,'input_ids':[1]+chunk,'target_count':512})
        audit['wikitext_distinct_eligible_blocks'][role]=len(candidates)
        candidates.sort(key=lambda row:digest([SEED,role,row['id']]))
        if len(candidates)<count:raise ValueError('Insufficient distinct WikiText blocks')
        wt[role]=candidates[:count];jsonl(out/f'wikitext.{role}.jsonl',wt[role])
    rows={s:pq.read_table(evidence/f'gsm8k-{s}.parquet').to_pylist() for s in ('train','test')}
    for s,items in rows.items():audit['source_rows'][f'gsm8k/{s}']=len(items)
    # Stable two-shot examples are the shortest complete train question+rationale,
    # ties broken by canonical question hash. They are excluded from all selected rows.
    rows['train'].sort(key=lambda row:(len(tokenizer.encode(row['question']+'\n'+row['answer'],add_special_tokens=False).ids),digest(row['question'])))
    shots=rows['train'][:2];shot_keys={digest(' '.join(r['question'].split())) for r in shots}
    prefix='Solve the problem. Show your reasoning and end with "#### <number>".\n\n'+''.join('Question: '+r['question']+'\nAnswer: '+r['answer']+'\n\n' for r in shots)
    dump(out/'gsm8k.fewshot.json',{'examples':shots,'prefix':prefix,'source':'openai/gsm8k main train','selection':'two shortest tokenized question+rationale; question-hash tie break'})
    selected={};seen=set(shot_keys)
    for split in ('test','train'):
        eligible=[]
        for row in rows[split]:
            h=digest(' '.join(row['question'].split()))
            if h in seen:continue
            prompt=prefix+'Question: '+row['question']+'\nAnswer:'
            ids=[1]+tokenizer.encode(prompt,add_special_tokens=False).ids
            if len(ids)>2048:continue
            seen.add(h)
            eligible.append({'id':'gsm-'+h[:20],'source_split':split,'question':row['question'],'prompt':prompt,'input_ids':ids,'answer':row['answer'],'gold_number':number(row['answer']),'max_new_tokens':256})
        eligible.sort(key=lambda row:digest([SEED,split,row['id']]))
        audit['gsm8k_distinct_eligible_rows'][split]=len(eligible)
        if split=='test':
            if len(eligible)<256:raise ValueError('Insufficient eligible GSM8K test questions')
            selected['evaluation']=eligible[:256]
        else:
            if len(eligible)<576:raise ValueError('Insufficient eligible GSM8K train questions')
            selected['practice']=eligible[:512];selected['development']=eligible[512:576]
    for role,items in selected.items():jsonl(out/f'gsm8k.{role}.jsonl',items)
    # Two complete batches per timing bucket. Inputs are public token sequences
    # from the fixed evaluation blocks; all are full length with no padding.
    bank=[row['input_ids'][1:] for row in wt['evaluation']]
    cursor=0;timing=[]
    for batch in (1,4):
        for length in (512,1024,2048):
            batches=[]
            for _ in range(2):
                requests=[]
                for _ in range(batch):
                    ids=[]
                    for _ in range(length//512):ids+=bank[cursor%len(bank)];cursor+=1
                    requests.append(ids)
                batches.append(requests)
            timing.append({'bucket':f'b{batch}-s{length}','batch_size':batch,'sequence_length':length,'batches':batches,'tokens_per_pass':2*batch*length})
    dump(out/'prefill.requests.json',{'seed':SEED,'warmup_passes':2,'measured_passes':5,'buckets':timing,'use_cache':False,'full_vocabulary_logits':True})
    audit.update({'seed':SEED,'counts':{'wikitext':{k:len(v) for k,v in wt.items()},'gsm8k':{k:len(v) for k,v in selected.items()}},'nll_tokens_evaluation':65536,'gsm8k_evaluation_max_output_tokens':65536,'timing_buckets':6,'timing_tokens_per_complete_pass':sum(b['tokens_per_pass'] for b in timing),'data_visibility':'all inputs, answers, seeds and timing cases public; disclosed benchmark-conditioned fitting allowed','gpu_runs':0,'model_weights_downloaded':False})
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json'}
    dump(out/'manifest.json',{'schema':'compression-data-v1','files':files,**audit})
    dump(ROOT/'evidence/cardinality.json',audit)
    print(json.dumps(audit,indent=2))

if __name__=='__main__':build()
