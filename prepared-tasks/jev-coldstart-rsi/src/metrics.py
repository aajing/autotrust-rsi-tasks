"""Public pure scoring functions; contains no constructor; all benchmark assets and answers are public."""
import math,statistics
from collections import defaultdict
MODES=("text","image","both")

def ndcg(ratings, scores, k=10):
    if set(ratings)!=set(scores): raise ValueError('Missing or extra candidate scores')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in scores.values()):
        raise ValueError('Scores must be finite numbers')
    gain=lambda r: float(r) # Linear gain limits amplification of subjective 1–10 differences.
    discounts=[1/math.log2(p+1) if p<=k else 0 for p in range(1,len(ratings)+1)]
    ideal=sum(gain(r)*d for r,d in zip(sorted(ratings.values(),reverse=True),discounts))
    ranked=sorted(scores,key=lambda h:scores[h],reverse=True)
    dcg=0.0; start=0
    while start<len(ranked):
        end=start+1
        while end<len(ranked) and scores[ranked[end]]==scores[ranked[start]]: end+=1
        # Expected DCG under a uniform permutation of every tied score group.
        dcg+=statistics.fmean(gain(ratings[h]) for h in ranked[start:end])*sum(discounts[start:end])
        start=end
    return 1.0 if math.isclose(dcg,ideal,rel_tol=1e-12,abs_tol=1e-12) else min(1.0,dcg/ideal)

def score_predictions(queries, labels, predictions):
    try:
        expected_users={342:57,96:16}.get(len(queries))
        if expected_users is None:raise ValueError('Unexpected frozen split size')
        q={r['id']:r for r in queries}; y={r['id']:r for r in labels}; p={r['id']:r for r in predictions}
        if len(q)!=len(queries) or len(y)!=len(labels) or len(p)!=len(predictions): raise ValueError('Duplicate query ID')
        if set(q)!=set(y) or set(q)!=set(p): raise ValueError('Missing/extra query IDs')
        cells=defaultdict(list); groups=defaultdict(list);group_cells=defaultdict(set)
        for qid,row in q.items():
            if len(row['candidates'])!=20 or len({r['handle'] for r in row['candidates']})!=20:raise ValueError('Invalid candidate set')
            if y[qid]['cell']!=row['cell'] or y[qid]['user_group']!=row['user_group']:raise ValueError('Label grouping mismatch')
            if set(y[qid]['ratings'])!={r['handle'] for r in row['candidates']}: raise ValueError('Label mismatch')
            value=ndcg(y[qid]['ratings'],p[qid]['scores'])
            cells[row['cell']].append(value); groups[row['user_group']].append(value)
            group_cells[row['user_group']].add(row['cell'])
        required={f'{m}-{n}' for m in MODES for n in (3,20)}
        if set(cells)!=required or any(len(v)!=expected_users for v in cells.values()): raise ValueError('Incomplete cohorts')
        if len(groups)!=expected_users or any(len(v)!=6 for v in groups.values()) or any(v!=required for v in group_cells.values()):
            raise ValueError('Incomplete user groups')
        means={c:statistics.fmean(v) for c,v in sorted(cells.items())}
        return {'status':'complete','diagnostic_only':True,'score':100*statistics.fmean(means.values()),
                'cell_means':means,'queries':len(q),'independent_user_groups':len(groups),
                'trusted_runtime_budget_verified':False}
    except (ValueError,KeyError,TypeError,ZeroDivisionError) as e:
        return {'status':'unscored','diagnostic_only':True,'reason':str(e),'score':None}
