"""CPU reward contract only. Inputs must come from the task-owned GPU evaluator.

Synthetic tests are not model measurements. This module never runs a model.
"""
import math
import re

KINDS=('noul','choice','score')
FAMILIES=('agent','biology','business','chemistry','genomics','knowledge','medical','physics','science','spatial','structured','technical','theology')

def _number(value, *, positive=False, probability=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('missing or non-finite metric')
    if value<0 or (positive and value<=0) or (probability and value>1):
        raise ValueError('metric outside physical range')
    return value

def _validate(report):
    if report.get('status')!='complete' or report.get('valid_artifact') is not True:
        raise ValueError('invalid or incomplete artifact')
    if report.get('system2_unchanged') is not True:
        raise ValueError('protected System 2 changed')
    if report.get('quality_rows')!=6144:
        raise ValueError('incomplete fixed evaluation cohort')
    if set(report['kind'])!=set(KINDS) or set(report['family_kl'])!=set(FAMILIES):
        raise ValueError('missing required primitive/family')
    for kind in KINDS:
        _number(report['kind'][kind]['kl'])
        _number(report['kind'][kind]['soft_ece10'],probability=True)
    for value in report['family_kl'].values():_number(value)
    for name in ('choice_agreement','noul_brier','score_rps'):
        _number(report[name],probability=True)
    for name in ('branch_bytes','gpu_peak_bytes'):_number(report[name],positive=True)
    if set(report['latency_ms'])!={'batch1','batch8'}:
        raise ValueError('missing latency workload')
    for value in report['latency_ms'].values():_number(value,positive=True)

def _bindings(candidate,reference):
    for name in ('data_manifest_sha256','runtime_fingerprint'):
        for report in (candidate,reference):
            value=report.get(name)
            if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):
                raise ValueError('missing or malformed protocol binding: '+name)
        if candidate[name]!=reference[name]:
            raise ValueError('protocol binding mismatch: '+name)

def score(candidate,reference):
    try:
        _validate(reference);_validate(candidate);_bindings(candidate,reference)
    except (ValueError,KeyError,TypeError,AttributeError) as exc:
        return {'status':'unscored','score':None,'reason':str(exc)}
    failures=[]
    for kind in KINDS:
        if candidate['kind'][kind]['kl']>reference['kind'][kind]['kl']+0.005:failures.append('kl:'+kind)
        if candidate['kind'][kind]['soft_ece10']>reference['kind'][kind]['soft_ece10']+0.005:failures.append('ece:'+kind)
    for family in FAMILIES:
        if candidate['family_kl'][family]>reference['family_kl'][family]+0.010:failures.append('family:'+family)
    if candidate['choice_agreement']<reference['choice_agreement']-0.01:failures.append('choice_agreement')
    if candidate['noul_brier']>reference['noul_brier']+0.001:failures.append('noul_brier')
    if candidate['score_rps']>reference['score_rps']+0.003:failures.append('score_rps')
    for name in reference['latency_ms']:
        if candidate['latency_ms'][name]>1.15*reference['latency_ms'][name]:failures.append('latency:'+name)
    if candidate['gpu_peak_bytes']>1.05*reference['gpu_peak_bytes']:failures.append('memory')
    if candidate['branch_bytes']>reference['branch_bytes']:
        return {'status':'unscored','score':None,'reason':'artifact exceeds allowed branch size'}
    reward=100*min(1,max(0,(1-candidate['branch_bytes']/reference['branch_bytes'])/0.75))
    return {'status':'scored','score':0.0 if failures else reward,'gate_failures':failures}
