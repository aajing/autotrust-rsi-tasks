"""Synthetic boundary/robustness checks; no claimed GPU measurements."""
import copy
import unittest
from scoring import score,KINDS,FAMILIES

def reference():
 return {'status':'complete','valid_artifact':True,'data_manifest_sha256':'0'*64,'runtime_fingerprint':'1'*64,'system2_unchanged':True,'quality_rows':6144,'kind':{k:{'kl':0.02,'soft_ece10':0.01} for k in KINDS},'family_kl':{f:0.02 for f in FAMILIES},'choice_agreement':0.9,'noul_brier':0.01,'score_rps':0.01,'branch_bytes':4000,'gpu_peak_bytes':1000,'latency_ms':{'batch1':100,'batch8':200}}
class ContractTests(unittest.TestCase):
 def setUp(self):self.b=reference();self.c=copy.deepcopy(self.b);self.c['branch_bytes']=1000
 def test_reference_is_zero(self):self.assertEqual(score(self.b,self.b)['score'],0)
 def test_full_target(self):self.assertEqual(score(self.c,self.b)['score'],100)
 def test_partial_size_gain(self):self.c['branch_bytes']=2500;self.assertEqual(score(self.c,self.b)['score'],50)
 def test_single_family_regression_cannot_be_averaged_away(self):self.c['family_kl']['medical']=0.031;self.assertEqual(score(self.c,self.b)['score'],0)
 def test_quality_boundary_is_inclusive(self):self.c['kind']['noul']['kl']=self.b['kind']['noul']['kl']+0.005;self.assertEqual(score(self.c,self.b)['score'],100)
 def test_invalid_is_not_zero(self):self.c['valid_artifact']=False;self.assertIsNone(score(self.c,self.b)['score'])
 def test_missing_row_is_unscored(self):self.c['quality_rows']=6143;self.assertIsNone(score(self.c,self.b)['score'])
 def test_nan_is_unscored(self):self.c['kind']['choice']['kl']=float('nan');self.assertIsNone(score(self.c,self.b)['score'])
 def test_timeout_unscored(self):self.c['status']='timeout';self.assertIsNone(score(self.c,self.b)['score'])
 def test_system2_change_invalid(self):self.c['system2_unchanged']=False;self.assertIsNone(score(self.c,self.b)['score'])
 def test_oversize_invalid(self):self.c['branch_bytes']=4001;self.assertIsNone(score(self.c,self.b)['score'])
 def test_latency_gate(self):self.c['latency_ms']['batch8']=231;self.assertEqual(score(self.c,self.b)['score'],0)

 def test_truthy_string_flag_is_invalid(self):self.c['valid_artifact']='false';self.assertIsNone(score(self.c,self.b)['score'])
 def test_missing_binding_is_unscored(self):del self.c['data_manifest_sha256'];self.assertIsNone(score(self.c,self.b)['score'])
 def test_changed_data_is_unscored(self):self.c['data_manifest_sha256']='2'*64;self.assertIsNone(score(self.c,self.b)['score'])
 def test_changed_runtime_is_unscored(self):self.c['runtime_fingerprint']='3'*64;self.assertIsNone(score(self.c,self.b)['score'])
 def test_truthy_system2_flag_invalid(self):self.c['system2_unchanged']='false';self.assertIsNone(score(self.c,self.b)['score'])
if __name__=='__main__':unittest.main()
