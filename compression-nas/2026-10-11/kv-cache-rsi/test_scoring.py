import copy,json,unittest
from pathlib import Path
from scoring import evaluate
SPEC=json.loads((Path(__file__).resolve().parent/'task.json').read_text())


def fixtures():
    names=[f'{n}x{b}' for n in [8192,16384,32256] for b in [1,4]] if SPEC['task_id']=='kv-cache-rsi' else ['batch1','batch8']
    base={'data_manifest_sha256':'d'*64,'runtime_fingerprint':'e'*64,'artifact_sha256':'a'*64,'quality_counts':{f:SPEC['data']['examples_per_family'] for f in SPEC['data']['families']},'quality_total':SPEC['data']['total_quality_examples'],'status':'complete','artifact_valid':True,'quality':{f:80 for f in SPEC['data']['families']},'cells':{n:{'elapsed_seconds':[3]*5,'gpu_peak_bytes':1000,'cache_bytes':[800]*129} for n in names}}
    if SPEC['task_id']=='kv-cache-rsi':
        base['quality_memory']={f:{i:{'prompt_tokens':1000,'generated_tokens':2,'decode_updates':1,'sample_count':2,'worst_dense_ratio':1.0} for i in SPEC['data']['evaluation_ids_by_family'][f]} for f in SPEC['data']['families']}
    if SPEC['task_id']=='vl-activation-quant-rsi':
        base.update(quality_processor_images=320,quality_vision_images=320)
        for cell in base['cells'].values():cell.update(processor_images=280,vision_images=280)
    cand=copy.deepcopy(base)
    if SPEC['task_id']=='kv-cache-rsi':
        for cell in cand['cells'].values():cell['cache_bytes']=[100]*129
        for rows in cand['quality_memory'].values():
            for entry in rows.values():entry['worst_dense_ratio']=.125
    else:
        cand.update(format_valid=True,actual_fp8_dispatch=True,static_parameter_coverage=.8,protected_bf16_parameter_fraction=.05)
        for cell in cand['cells'].values():cell.update(elapsed_seconds=[2]*5,gpu_peak_bytes=700)
    return cand,base


class RewardTests(unittest.TestCase):
    def test_full_score_boundary(self):
        c,b=fixtures();r=evaluate(c,b,SPEC);self.assertEqual(r['status'],'scored');self.assertAlmostEqual(r['score'],100)
    def test_one_family_cannot_hide_behind_macro(self):
        c,b=fixtures();c['quality'][SPEC['data']['families'][0]]=70
        for f in SPEC['data']['families'][1:]:c['quality'][f]=90
        r=evaluate(c,b,SPEC);self.assertEqual(r['score'],0);self.assertFalse(r['gates']['quality_every_family'])
    def test_invalid_incomplete_and_nan_are_unscored(self):
        for kind in ['crash','missing','nan']:
            c,b=fixtures()
            if kind=='crash':c['status']='candidate_process_crash'
            elif kind=='missing':c['cells'].pop(next(iter(c['cells'])))
            else:c['quality'][SPEC['data']['families'][0]]=float('nan')
            r=evaluate(c,b,SPEC);self.assertEqual(r['status'],'unscored');self.assertIsNone(r['score'])
    def test_worst_cell_and_repeat_completeness(self):
        c,b=fixtures();cell=c['cells'][next(iter(c['cells']))];cell['gpu_peak_bytes']=2000
        self.assertEqual(evaluate(c,b,SPEC)['score'],0)
        cell['elapsed_seconds'].pop();self.assertIsNone(evaluate(c,b,SPEC)['score'])
    def test_identity_is_zero(self):
        c,b=fixtures();c['identity_baseline']=True;c['artifact_sha256']=b['artifact_sha256'];self.assertEqual(evaluate(c,b,SPEC)['score'],0)
    def test_bindings_and_quality_coverage(self):
        for key in ['data_manifest_sha256','runtime_fingerprint']:
            c,b=fixtures();c[key]='f'*64;self.assertIsNone(evaluate(c,b,SPEC)['score'])
            c[key]='';self.assertIsNone(evaluate(c,b,SPEC)['score'])
        c,b=fixtures();c['quality_counts'][SPEC['data']['families'][0]]-=1
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
        c,b=fixtures();c['quality_total']-=1;self.assertIsNone(evaluate(c,b,SPEC)['score'])
    def test_identity_still_requires_complete_cells_and_digest(self):
        c,b=fixtures();c['identity_baseline']=True;c['cells'].pop(next(iter(c['cells'])))
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
        c,b=fixtures();c['identity_baseline']=True;c['artifact_sha256']='f'*64
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
    def test_quality_workload_cache_is_not_exempt(self):
        if SPEC['task_id']!='kv-cache-rsi':return
        c,b=fixtures();family=SPEC['data']['families'][0];rows=c['quality_memory'][family];entry=rows[next(iter(rows))];entry['worst_dense_ratio']=1.0
        self.assertEqual(evaluate(c,b,SPEC)['score'],0)
        entry['worst_dense_ratio']=.125;entry['sample_count']=1
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
        rows.pop(next(iter(rows)));self.assertIsNone(evaluate(c,b,SPEC)['score'])
    def test_multimodal_cache_cannot_skip_work(self):
        if SPEC['task_id']!='vl-activation-quant-rsi':return
        c,b=fixtures();c['cells']['batch1']['vision_images']=40
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
        c,b=fixtures();c['quality_processor_images']=319
        self.assertIsNone(evaluate(c,b,SPEC)['score'])
    def test_task_specific_runtime_boundaries(self):
        c,b=fixtures()
        if SPEC['task_id']=='kv-cache-rsi':
            c['cells']['32256x4']['cache_bytes'][-1]=400
            self.assertAlmostEqual(evaluate(c,b,SPEC)['score'],100*.5/.875)
        else:
            c['static_parameter_coverage']=.79
            self.assertIsNone(evaluate(c,b,SPEC)['score'])
            c['static_parameter_coverage']=.8;c['actual_fp8_dispatch']=False
            self.assertIsNone(evaluate(c,b,SPEC)['score'])

if __name__=='__main__':unittest.main()
