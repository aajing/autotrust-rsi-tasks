"""CPU-only reward oracle for task-owned measurements; this is not a GPU evaluator.

Only the fixed Judge may issue artifact_valid / identity_baseline / format audits.
This function does not establish artifact integrity from candidate assertions.
"""
import json
import math
import re
from pathlib import Path
import statistics
import sys


def number(value, *, low=0, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('nonfinite or nonnumeric measurement')
    if value < low or (high is not None and value > high):
        raise ValueError('measurement outside defined range')
    return float(value)


def positive(value):
    out = number(value)
    if out <= 0:
        raise ValueError('nonpositive reference/time/peak')
    return out


def median_time(cell):
    values = cell['elapsed_seconds']
    if not isinstance(values, list) or len(values) != 5:
        raise ValueError('expected exactly five complete timed repeats')
    return statistics.median(positive(x) for x in values)


def clip(value):
    return min(1., max(0., value))


def evaluate(candidate, reference, spec):
    try:
        for value in (candidate, reference):
            if value.get('status') != 'complete' or value.get('artifact_valid') is not True:
                return {'status': 'unscored', 'score': None, 'reason': 'invalid, failed, or incomplete evaluation'}
        for key in ('data_manifest_sha256', 'runtime_fingerprint'):
            for record in (candidate, reference):
                if not isinstance(record.get(key), str) or not re.fullmatch(r'[0-9a-f]{64}', record[key]):
                    raise ValueError('missing or invalid binding: '+key)
            if candidate[key] != reference[key]:
                raise ValueError('candidate/reference binding mismatch: '+key)
        for record in (candidate, reference):
            if not isinstance(record.get('artifact_sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', record['artifact_sha256']):
                raise ValueError('missing artifact identity digest')
        identity = candidate.get('identity_baseline') is True
        if identity and candidate['artifact_sha256'] != reference['artifact_sha256']:
            raise ValueError('claimed B0 identity without matching artifact digest')
        fams = spec['data']['families']
        expected_counts = {f:spec['data']['examples_per_family'] for f in fams}
        for record in (candidate, reference):
            if record.get('quality_counts') != expected_counts or any(type(n) is not int for n in record['quality_counts'].values()):
                raise ValueError('incomplete or wrong quality family counts')
            if type(record.get('quality_total')) is not int or record['quality_total'] != spec['data']['total_quality_examples']:
                raise ValueError('incomplete total quality coverage')
        if set(candidate['quality']) != set(fams) or set(reference['quality']) != set(fams):
            raise ValueError('quality family mismatch')
        drops = {f: number(reference['quality'][f], high=100)-number(candidate['quality'][f], high=100) for f in fams}
        macro_drop = sum(drops.values()) / len(fams)
        gates = {'quality_macro': macro_drop <= spec['score']['quality_macro_drop_pp_max'] + 1e-12,
                 'quality_every_family': max(drops.values()) <= spec['score']['quality_each_family_drop_pp_max'] + 1e-12}
        if spec['task_id'] == 'kv-cache-rsi':
            names = [f'{n}x{b}' for n in spec['performance_protocol']['prompt_lengths'] for b in spec['performance_protocol']['batch_sizes']]
        else:
            if not identity:
                if candidate.get('format_valid') is not True or candidate.get('actual_fp8_dispatch') is not True:
                    raise ValueError('unsupported format or missing actual FP8 execution')
                static = number(candidate['static_parameter_coverage'], high=1)
                protected = number(candidate['protected_bf16_parameter_fraction'], high=1)
                if static < spec['allowed_candidate']['static_parameter_coverage_min']-1e-12 or protected > spec['allowed_candidate']['protected_bf16_parameter_fraction_max']+1e-12 or static+protected > 1+1e-12:
                    raise ValueError('activation coverage or protected fraction violation')
            names = ['batch1', 'batch8']
            for record in (candidate, reference):
                for key in ('quality_processor_images','quality_vision_images'):
                    if type(record.get(key)) is not int or record[key] != 320:
                        raise ValueError('missing quality image execution coverage')
        if set(candidate['cells']) != set(names) or set(reference['cells']) != set(names):
            raise ValueError('missing or extra performance cell')
        ratios, peaks, cache_ratios = [], [], []
        if spec['task_id'] == 'kv-cache-rsi':
            expected_ids = spec['data']['evaluation_ids_by_family']
            for record in (candidate, reference):
                if set(record['quality_memory']) != set(fams):
                    raise ValueError('missing quality-memory family')
                for family in fams:
                    rows = record['quality_memory'][family]
                    if set(rows) != set(expected_ids[family]):
                        raise ValueError('quality-memory ID coverage mismatch')
                    for entry in rows.values():
                        for key in ('prompt_tokens','generated_tokens','decode_updates','sample_count'):
                            if type(entry[key]) is not int:
                                raise ValueError('invalid quality-memory count type')
                        p,g = entry['prompt_tokens'],entry['generated_tokens']
                        if p < 1 or g < 1 or g > spec['generation']['max_new_tokens'][family] or p+g > 32768 or entry['decode_updates'] != g-1 or entry['sample_count'] != g:
                            raise ValueError('incomplete quality-memory token/update audit')
                        ratio = number(entry['worst_dense_ratio'])
                        if record is candidate:
                            cache_ratios.append(ratio)
        for name in names:
            c, b = candidate['cells'][name], reference['cells'][name]
            if spec['task_id'] == 'vl-activation-quant-rsi':
                for cell in (c,b):
                    for key in ('processor_images','vision_images'):
                        if type(cell.get(key)) is not int or cell[key] != 280:
                            raise ValueError('missing multimodal execution coverage')
            ratios.append(median_time(c)/median_time(b))
            peaks.append(positive(c['gpu_peak_bytes'])/positive(b['gpu_peak_bytes']))
            if spec['task_id'] == 'kv-cache-rsi':
                cv, bv = c['cache_bytes'], b['cache_bytes']
                if len(cv) != 129 or len(bv) != 129:
                    raise ValueError('expected post-prefill plus128 decode memory samples')
                cache_ratios.extend(number(x)/positive(y) for x,y in zip(cv,bv))
        if identity:
            return {'status':'scored','score':0.,'reason':'hash-verified unchanged B0 identity with complete measurements','family_drops_pp':drops}
        latency = math.exp(sum(math.log(x) for x in ratios)/len(ratios))
        if spec['task_id'] == 'kv-cache-rsi':
            cache = max(cache_ratios)
            gates.update(latency_geomean=latency<=spec['score']['latency_geomean_ratio_max']+1e-12,
                         latency_every_cell=max(ratios)<=spec['score']['latency_each_cell_ratio_max']+1e-12,
                         peak_gpu=max(peaks)<=spec['score']['peak_gpu_ratio_max']+1e-12)
            raw=100*clip((1-cache)/.875)
            details={'worst_cache_ratio':cache,'latency_geomean_ratio':latency}
        else:
            speed=1/latency
            gates.update(no_batch_slowdown=max(ratios)<=1+1e-12,
                         peak_gpu=max(peaks)<=spec['score']['peak_gpu_ratio_max']+1e-12)
            raw=100*clip((speed-1)/.5)
            details={'throughput_geomean_speedup':speed}
        return {'status':'scored','score':raw if all(gates.values()) else 0.,'gates':gates,
                'quality_macro_drop_pp':macro_drop,'family_drops_pp':drops,'worst_peak_gpu_ratio':max(peaks),**details}
    except (KeyError, ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        return {'status':'unscored','score':None,'reason':str(exc)}


if __name__=='__main__':
    if len(sys.argv)!=3:
        raise SystemExit('Usage: python scoring.py candidate-metrics.json reference-metrics.json')
    root=Path(__file__).resolve().parent
    result=evaluate(json.loads(Path(sys.argv[1]).read_text()),json.loads(Path(sys.argv[2]).read_text()),json.loads((root/'task.json').read_text()))
    print(json.dumps(result,indent=2,allow_nan=False))
