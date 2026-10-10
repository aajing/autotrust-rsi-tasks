"""CPU contract arithmetic over operator-captured metrics, not an official Judge.

No model loading, GPU execution, resource attestation or self-reported reward.
"""
import math
import statistics

BUCKETS=tuple(f"b{batch}-s{length}" for batch in (1,4) for length in (512,1024,2048))
class ContractError(ValueError):pass

def finite(value,name,minimum=0):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<minimum:
        raise ContractError("invalid "+name)
    return float(value)

def validate(record):
    if record.get('status')!='complete' or record.get('admission')!='passed':raise ContractError('incomplete or invalid artifact')
    if record.get('nll_token_count')!=65536 or record.get('gsm_count')!=256:raise ContractError('evaluation coverage mismatch')
    if not record.get('data_manifest_sha256') or not record.get('runtime_fingerprint'):raise ContractError('missing data/runtime binding')
    finite(record.get('mean_nll'),'mean_nll');finite(record.get('gsm_correct'),'gsm_correct')
    if type(record['gsm_correct']) is not int or record['gsm_correct']>256:raise ContractError('invalid correct count')
    finite(record.get('model_tensor_bytes'),'model_tensor_bytes',1)
    finite(record.get('peak_gpu_bytes'),'peak_gpu_bytes',1)
    if finite(record.get('judge_wall_seconds'),'judge_wall_seconds')>2700:raise ContractError('Judge timeout')
    timing=record.get('prefill_ms',{})
    if set(timing)!=set(BUCKETS):raise ContractError('missing timing bucket')
    for name,passes in timing.items():
        if not isinstance(passes,list) or len(passes)!=5:raise ContractError('five timed passes required')
        for item in passes:finite(item,name,0.000001)
    return record

def score(kind,candidate,reference):
    if kind not in ('lowrank','sparse24'):raise ContractError('unknown contract')
    c=validate(candidate);b=validate(reference)
    for key in ('data_manifest_sha256','runtime_fingerprint'):
        if c[key]!=b[key]:raise ContractError('incompatible '+key)
    ratio=c['model_tensor_bytes']/b['model_tensor_bytes']
    speeds={name:statistics.median(b['prefill_ms'][name])/statistics.median(c['prefill_ms'][name]) for name in BUCKETS}
    speed=math.exp(sum(math.log(v) for v in speeds.values())/len(speeds))
    gates={'language_quality':c['mean_nll']<=b['mean_nll']+0.10+1e-12,
           'math_quality':c['gsm_correct']/256+1e-12>=b['gsm_correct']/256-0.03,
           'peak_gpu':c['peak_gpu_bytes']<=64*1024**3}
    if kind=='lowrank':
        gates.update({'no_storage_growth':ratio<=1,'prefill_regression':all(v>=0.90-1e-12 for v in speeds.values())})
        raw=100*max(0,min(1,(1-ratio)/0.40))
    else:
        if type(c.get('sparse_modules')) is not int or not 0<=c['sparse_modules']<=224:raise ContractError('invalid sparse module count')
        if c['sparse_modules'] and c.get('sparse_dispatch_verified') is not True:raise ContractError('native sparse dispatch was not verified')
        gates['per_bucket_regression']=all(v>=0.95-1e-12 for v in speeds.values())
        raw=100*max(0,min(1,(speed-1.03)/(1.25-1.03))) if c["sparse_modules"] else 0.0
    return {'status':'scored_assessment','official_reward':False,'score':raw if all(gates.values()) else 0.0,'gates':gates,'tensor_byte_ratio':ratio,'prefill_speedup_geomean':speed,'per_bucket_speedup':speeds}
