#!/usr/bin/env python3
"""Check proposal format and synchronize package copies; no external writes."""
import datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DRAFTS=ROOT.parent/'draft-proposals/2026-10-10'
TASKS=('gev-think-rsi','jev-judge-rsi','jev-coldstart-rsi','jev-visual-control-rsi','gev-quant-rsi','moe-prune-rsi')
schema=json.loads((DRAFTS/'evidence/proposal-fields.json').read_text())
files=[]
for name in TASKS:
    p=DRAFTS/(name+'.md');body=p.read_text()
    rows=[]
    for line in body.splitlines():
        if not line.startswith('|'):continue
        cells=[c.strip() for c in line.strip('|').split('|')]
        if len(cells)!=3:raise ValueError('Malformed table row: '+name)
        if cells[0] in ('Section','---'):continue
        rows.append(cells)
    if [[r[0],r[1]] for r in rows]!=schema:raise ValueError('Official field mismatch: '+name)
    if re.search('[\u4e00-\u9fff]',body):raise ValueError('Non-English official proposal: '+name)
    if 'not submitted' not in body.lower():raise ValueError('Submission marker missing: '+name)
    if not re.search(r'full (score|marks)',body,re.I):raise ValueError('Full-score rule missing: '+name)
    if 'Jing Qiu' not in body or 'ajing@autotrust.ai' not in body:raise ValueError('Contributor mismatch: '+name)
    if re.search(r'\]\(https?://github\.com/',body):raise ValueError('GitHub URL should be plain code text: '+name)
    (ROOT/name/'proposal.md').write_text(body)
    files.append({'file':p.name,'sha256':hashlib.sha256(body.encode()).hexdigest(),'word_count':len(body.split()),
                  'official_fields':len(rows),'english_only':True,'explicit_full_score':True,'marked_not_submitted':True,
                  'package_copy_identical':True})
report={'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'28-field format, English text, contributor identity, plain GitHub URLs and package-copy consistency; CPU checks recorded separately',
        'submission_status':'not submitted to official review; public publication tracked separately',
        'current_official_template_blob':'0f8d6537a413156eb286a0ca66e09b6491291a5f','files':files,
        'preparation_changes':['Host RAM availability confirmed by user','Five open procedural datasets and CPU contracts materialized',
                               'Recommendation dataset changed to CC0 Simulacra with acquired source metadata and fixed six-cohort split',
                               'All prepared evaluation answers, seeds and reference materials public and unencrypted',
                               'Judge lexical shortcuts removed and independent world coverage expanded',
                               'Prune full-score expert-removal threshold raised to 37.5%',
                               'Source pins, baseline materializers, scoring contracts and runbooks prepared'],
        'not_performed':['Official proposal submission','GPU/model inference or training','Full Simulacra image archive download',
                         'H100 runtime/latency measurements','Official trusted Harness activation']}
(DRAFTS/'evidence/document-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'proposals_checked':len(files),'fields_each':28,'english_only':True,'submitted':False}))
