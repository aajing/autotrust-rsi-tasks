"""CPU reward contract; consumes trusted evaluator reports, not candidate claims."""
import math
import re
CELLS=('wiki256','wiki512','wiki1024','tiny256','tiny512','tiny1024')
WORKLOADS=('b1l128','b4l512','b8l1024')

def _number(value,positive=False):
 if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or (positive and value<=0):raise ValueError('missing/non-finite/nonphysical metric')
 return value

def _validate(report):
 if report.get('status')!='complete' or report.get('valid_artifact') is not True:raise ValueError('invalid or incomplete artifact')
 if report.get('data_complete') is not True:raise ValueError('incomplete fixed token corpus')
 if set(report['nll'])!=set(CELLS) or set(report['latency_ms'])!=set(WORKLOADS):raise ValueError('missing domain/context or latency workload')
 for v in report['nll'].values():_number(v)
 for v in report['latency_ms'].values():_number(v,True)
 for name in ('tensor_bytes','gpu_peak_bytes'):_number(report[name],True)

def _bindings(candidate,reference):
    for name in ('data_manifest_sha256','runtime_fingerprint'):
        for report in (candidate,reference):
            value=report.get(name)
            if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):
                raise ValueError('missing or malformed protocol binding: '+name)
        if candidate[name]!=reference[name]:
            raise ValueError('protocol binding mismatch: '+name)

def score(candidate,reference):
 try:_validate(reference);_validate(candidate);_bindings(candidate,reference)
 except (ValueError,KeyError,TypeError,AttributeError) as exc:return {'status':'unscored','score':None,'reason':str(exc)}
 failures=[]
 for cell in CELLS:
  if candidate['nll'][cell]>reference['nll'][cell]+0.08:failures.append('nll:'+cell)
 ratios=[]
 for name in WORKLOADS:
  r=candidate['latency_ms'][name]/reference['latency_ms'][name];ratios.append(r)
  if r>1.05:failures.append('latency:'+name)
 if candidate['gpu_peak_bytes']>1.05*reference['gpu_peak_bytes']:failures.append('memory')
 ratio=math.exp(sum(math.log(r) for r in ratios)/3)
 s=candidate['tensor_bytes']/reference['tensor_bytes']
 gain=min(min(1,max(0,(1-s)/0.30)),min(1,max(0,(1-ratio)/0.40)))
 return {'status':'scored','score':0.0 if failures else 100*gain,'gate_failures':failures,'latency_ratio_gmean':ratio,'bytes_ratio':s}
