import copy,math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import ROOT,ndcg,read_jsonl,score_predictions,split_paths

class ContractTests(unittest.TestCase):
    def setUp(self):
        q,y=split_paths(ROOT,'dev');self.q=read_jsonl(q);self.y=read_jsonl(y)
        self.p=[{'id':r['id'],'scores':dict(r['ratings'])} for r in self.y]
    def test_oracle_score(self):
        self.assertAlmostEqual(score_predictions(self.q,self.y,self.p)['score'],100)
    def test_reverse_is_worse(self):
        p=[{'id':r['id'],'scores':{k:-v for k,v in r['ratings'].items()}} for r in self.y]
        self.assertLess(score_predictions(self.q,self.y,p)['score'],100)
    def test_ties_are_expected_discount(self):
        expected=((10+1)/2)*(1+1/math.log2(3))/(10+1/math.log2(3))
        self.assertAlmostEqual(ndcg({'a':10,'b':1},{'a':0,'b':0}),expected)
        self.assertEqual(ndcg({'a':10,'b':10},{'a':0,'b':0}),1)
    def test_invalid_coverage_and_numbers(self):
        for p in (self.p[:-1],self.p+self.p[:1]):self.assertEqual(score_predictions(self.q,self.y,p)['status'],'unscored')
        for bad in (float('nan'),float('inf'),True,'1'):
            p=copy.deepcopy(self.p);p[0]['scores']['c0']=bad
            self.assertEqual(score_predictions(self.q,self.y,p)['status'],'unscored')
        p=copy.deepcopy(self.p);del p[0]['scores']['c0']
        self.assertEqual(score_predictions(self.q,self.y,p)['status'],'unscored')
    def test_truncated_whole_context_is_unscored(self):
        self.assertEqual(score_predictions(self.q[:6],self.y[:6],self.p[:6])['status'],'unscored')
        q=copy.deepcopy(self.q)
        for r in q:r['user_group']=q[0]['user_group']
        self.assertEqual(score_predictions(q,self.y,self.p)['status'],'unscored')
    def test_split_and_modality(self):
        users={};assets={}
        for split,count in [('train',342),('dev',96),('evaluation',96)]:
            qp,yp=split_paths(ROOT,split);qs=read_jsonl(qp);self.assertEqual(len(qs),count)
            users[split]={q['user_group'] for q in qs};assets[split]=set()
            for q in qs:
                mode,n=q['cell'].split('-');self.assertEqual(len(q['history']),int(n));self.assertEqual(len(q['candidates']),20)
                for r in q['history']+q['candidates']:
                    self.assertEqual('image' in r,mode in ('image','both'));self.assertEqual('text' in r,mode in ('text','both'))
                    if 'image' in r:assets[split].add(r['image'])
                self.assertTrue(all('rating' not in r for r in q['candidates']))
        for a,b in [('train','dev'),('train','evaluation'),('dev','evaluation')]:
            self.assertFalse(users[a]&users[b]);self.assertFalse(assets[a]&assets[b])

if __name__=='__main__':unittest.main()
