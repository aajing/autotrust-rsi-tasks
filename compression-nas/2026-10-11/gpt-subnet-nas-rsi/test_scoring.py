"""Synthetic score semantics, missing-data and separate-family robustness checks."""
import copy
import unittest
from scoring import score,CELLS,WORKLOADS

def reference():return {'status':'complete','valid_artifact':True,'data_manifest_sha256':'0'*64,'runtime_fingerprint':'1'*64,'data_complete':True,'nll':{x:3.0 for x in CELLS},'latency_ms':{x:100 for x in WORKLOADS},'tensor_bytes':1000,'gpu_peak_bytes':1000}
class ContractTests(unittest.TestCase):
 def setUp(self):self.b=reference();self.c=copy.deepcopy(self.b);self.c['tensor_bytes']=700;self.c['latency_ms']={x:60 for x in WORKLOADS}
 def test_baseline_zero(self):self.assertEqual(score(self.b,self.b)['score'],0)
 def test_full_score_requires_both(self):self.assertAlmostEqual(score(self.c,self.b)['score'],100)
 def test_storage_alone_insufficient(self):self.c['latency_ms']=self.b['latency_ms'];self.assertEqual(score(self.c,self.b)['score'],0)
 def test_speed_alone_insufficient(self):self.c['tensor_bytes']=1000;self.assertEqual(score(self.c,self.b)['score'],0)
 def test_worst_domain_gate(self):self.c['nll']['wiki1024']=3.081;self.assertEqual(score(self.c,self.b)['score'],0)
 def test_missing_domain_unscored(self):del self.c['nll']['tiny256'];self.assertIsNone(score(self.c,self.b)['score'])
 def test_crash_unscored(self):self.c['status']='candidate_crash';self.assertIsNone(score(self.c,self.b)['score'])
 def test_nonfinite_unscored(self):self.c['nll']['wiki256']=float('inf');self.assertIsNone(score(self.c,self.b)['score'])
 def test_zero_latency_invalid(self):self.c['latency_ms']['b1l128']=0;self.assertIsNone(score(self.c,self.b)['score'])
 def test_one_workload_regression_not_hidden(self):self.c['latency_ms']['b1l128']=106;self.assertEqual(score(self.c,self.b)['score'],0)
 def test_partial_gain(self):self.c['tensor_bytes']=850;self.c['latency_ms']={x:80 for x in WORKLOADS};self.assertAlmostEqual(score(self.c,self.b)['score'],50)
 def test_incomplete_data_unscored(self):self.c['data_complete']=False;self.assertIsNone(score(self.c,self.b)['score'])

 def test_truthy_string_flag_is_invalid(self):self.c['valid_artifact']='false';self.assertIsNone(score(self.c,self.b)['score'])
 def test_missing_binding_is_unscored(self):del self.c['data_manifest_sha256'];self.assertIsNone(score(self.c,self.b)['score'])
 def test_changed_data_is_unscored(self):self.c['data_manifest_sha256']='2'*64;self.assertIsNone(score(self.c,self.b)['score'])
 def test_changed_runtime_is_unscored(self):self.c['runtime_fingerprint']='3'*64;self.assertIsNone(score(self.c,self.b)['score'])
if __name__=='__main__':unittest.main()
