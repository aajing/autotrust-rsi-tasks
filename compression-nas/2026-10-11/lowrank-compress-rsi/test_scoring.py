"""Synthetic arithmetic checks. No fixture is a measured model score."""
import copy
import unittest
from scoring import BUCKETS,ContractError,score

def fixture():
    return {'status':'complete','admission':'passed','nll_token_count':65536,'gsm_count':256,'data_manifest_sha256':'synthetic-data-hash','runtime_fingerprint':'synthetic-runtime','mean_nll':2.0,'gsm_correct':128,'model_tensor_bytes':1000,'peak_gpu_bytes':1024,'judge_wall_seconds':30,'prefill_ms':{k:[10.0]*5 for k in BUCKETS},'sparse_modules':0,'sparse_dispatch_verified':False}

class ScoringContracts(unittest.TestCase):
    def test_identity_and_lowrank_endpoints(self):
        b=fixture();self.assertEqual(score('lowrank',b,b)['score'],0)
        c=copy.deepcopy(b);c['model_tensor_bytes']=800;self.assertAlmostEqual(score('lowrank',c,b)['score'],50)
        c['model_tensor_bytes']=600;self.assertEqual(score('lowrank',c,b)['score'],100)
    def test_sparse_real_speed_required(self):
        b=fixture();self.assertEqual(score('sparse24',b,b)['score'],0)
        c=copy.deepcopy(b);c.update(sparse_modules=64,sparse_dispatch_verified=True)
        self.assertEqual(score('sparse24',c,b)['score'],0)
        c['prefill_ms']={k:[8.0]*5 for k in BUCKETS};self.assertEqual(score('sparse24',c,b)['score'],100)
        c['sparse_dispatch_verified']=False
        with self.assertRaises(ContractError):score('sparse24',c,b)
    def test_quality_gate_is_finite_zero(self):
        b=fixture();c=copy.deepcopy(b);c['model_tensor_bytes']=600;c['mean_nll']=2.101
        self.assertEqual(score('lowrank',c,b)['score'],0)
        c['mean_nll']=2.0;c['gsm_correct']=120
        self.assertEqual(score('lowrank',c,b)['score'],0)
    def test_coverage_and_binding_rejected(self):
        b=fixture()
        for key,value in [('nll_token_count',65535),('gsm_count',255),('runtime_fingerprint','different'),('data_manifest_sha256','changed')]:
            c=copy.deepcopy(b);c[key]=value
            with self.assertRaises(ContractError):score('lowrank',c,b)
    def test_bad_timing_and_timeout_rejected(self):
        b=fixture();c=copy.deepcopy(b);c['prefill_ms'][BUCKETS[0]][0]=float('nan')
        with self.assertRaises(ContractError):score('sparse24',c,b)
        c=copy.deepcopy(b);c['judge_wall_seconds']=2701
        with self.assertRaises(ContractError):score('lowrank',c,b)
    def test_single_bucket_regression_cannot_hide_in_average(self):
        b=fixture();c=copy.deepcopy(b);c.update(sparse_modules=224,sparse_dispatch_verified=True);c['prefill_ms']={k:[5.0]*5 for k in BUCKETS};c['prefill_ms'][BUCKETS[0]]=[11.0]*5
        self.assertEqual(score('sparse24',c,b)['score'],0)
if __name__=='__main__':unittest.main()
