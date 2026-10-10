"""Synthetic CPU fixtures validate contracts, not model quality or GPU feasibility."""
import copy
import tempfile
import unittest
from pathlib import Path
import numpy as np
from taskkit.common import FAMILIES,ContractError,SOURCE_REVISION,paths,read_json,read_jsonl
from taskkit.data import audit,group_split
from taskkit.oracles import check_python,check_sql,evaluate_answer
from taskkit.scoring import aggregate,compose,total_variation,validate_reference
from taskkit.tensors import quantize,dequantize,float_to_bf16,bf16_to_float,validate_expert_map,frequency_map,construct_pruned_layer,admit_pruned_layer,select_expert_tensors
from taskkit.accounting import validate_ledger

ROOT=Path(__file__).resolve().parents[1]

class Contracts(unittest.TestCase):
    def test_counts_groups_and_hashes(self):
        result=audit(ROOT)
        self.assertEqual(result["status"],"pass")
        cfg=read_json(ROOT/"task.json")
        self.assertEqual(result["unique_scenario_groups"],sum(cfg["counts"].values()))

    def test_public_release_assets(self):
        cfg=read_json(ROOT/"task.json")
        self.assertEqual(cfg["benchmark_visibility"],"public")
        for split in ("practice","development","evaluation"):
            for path in paths(ROOT,split):
                self.assertTrue(path.is_file())
                self.assertTrue(path.is_relative_to(ROOT/"data/public"))
        self.assertEqual(len(read_json(ROOT/"public-authoring/evaluation_seed.json")["seed_hex"]),32)
        if cfg["mode"]=="prune":
            plan=read_json(ROOT/"public-authoring/b96_profile_plan.json")
            practice={r["id"] for r in read_jsonl(paths(ROOT,"practice")[0])}
            self.assertEqual(len(set(plan["ids"])),384)
            self.assertTrue(set(plan["ids"])<=practice)

    def test_all_oracles(self):
        total=0
        for split in ("practice","development","evaluation"):
            ip,gp=paths(ROOT,split);inputs=read_jsonl(ip);golds=read_jsonl(gp)
            predictions=[{"id":g["id"],"output":g["canonical_output"]} for g in golds]
            result=aggregate(inputs,golds,predictions)
            self.assertEqual(result["accuracy"],1.0)
            self.assertEqual(result["brier"],0.0)
            total+=result["count"]
        self.assertEqual(total,sum(read_json(ROOT/"task.json")["counts"].values()))

    def test_duplicate_missing_extra_coverage(self):
        ip,gp=paths(ROOT,"development");inputs=read_jsonl(ip);gold=read_jsonl(gp)
        good=[{"id":g["id"],"output":g["canonical_output"]} for g in gold]
        for bad in (good[:-1],good+[good[0]],good+[{"id":"extra","output":0}]):
            with self.assertRaises(ContractError):aggregate(inputs,gold,bad)

    def test_bad_outputs_stay_in_denominator(self):
        ip,gp=paths(ROOT,"development");inputs=read_jsonl(ip);gold=read_jsonl(gp)
        bad=[{"id":g["id"],"output":"not a valid answer"} for g in gold]
        result=aggregate(inputs,gold,bad)
        self.assertEqual(result["accuracy"],0)
        self.assertEqual(result["brier"],1)

    def test_python_rejects_host_execution_and_resource_bombs(self):
        tests=[{"input":[1,2],"output":3}]
        self.assertTrue(check_python("def solve(xs):\n return sum(xs)",tests))
        for text in ["def solve(xs):\n return __import__('os').system('id')",
                     "def solve(xs):\n return [0] * 1000000",
                     "def solve(xs):\n return sum(sum(x for x in xs) for x in xs)",
                     "def solve(xs):\n while True: pass",
                     "import os\ndef solve(xs): return 3"]:
            self.assertFalse(check_python(text,tests))

    def test_sql_rejects_writes(self):
        db=[{"rows":[[1,"east",3,2,1,5,1]],"output":[[7]]}]
        self.assertTrue(check_sql("SELECT SUM(amount*quantity+fee) FROM orders",db))
        self.assertFalse(check_sql("DELETE FROM orders",db))
        self.assertFalse(check_sql("SELECT load_extension('x')",db))

    def test_quant_dtype_shape_padding_rounding(self):
        rng=np.random.default_rng(27)
        for group in (32,64,128):
            for bits in (4,8):
                x=rng.normal(size=(3,70)).astype(np.float32)
                q=quantize(x,bits,group);y=dequantize(q)
                self.assertEqual(y.dtype,x.dtype);self.assertEqual(y.shape,x.shape)
                self.assertLessEqual(float(np.max(np.abs(x-y))),float(q["scales"].max())*0.501+1e-5)
                bad=copy.deepcopy(q);bad["scales"]=bad["scales"].astype(np.float64)
                with self.assertRaises(ContractError):dequantize(bad)
        # Exact ties-even and signed two's-complement packing.
        x=np.zeros((1,32),np.float32);x[0,:6]=[-7,-2.5,-1.5,1.5,2.5,7]
        q=quantize(x,4,32);self.assertEqual(dequantize(q)[0,:6].tolist(),[-7,-2,-2,2,2,7])
        self.assertEqual(int(q["values"][0])&15,9)
        bad=copy.deepcopy(q);bad["values"][0]=8
        with self.assertRaises(ContractError):dequantize(bad)
        z=quantize(np.zeros((2,33),np.float32),4,32)
        self.assertTrue(np.array_equal(dequantize(z),np.zeros((2,33),np.float32)))
        with self.assertRaises(ContractError):quantize(x.astype(np.float64))


    def test_quant_recipe_scope(self):
        from taskkit.tensors import make_quant_plan,validate_quant_plan,quantize_expert_tensor
        index=read_json(ROOT/"source/metadata/model.safetensors.index.json")
        plan=make_quant_plan(index["weight_map"])
        self.assertTrue(validate_quant_plan(plan,index["weight_map"]))
        bad=copy.deepcopy(plan)
        bad["per_expert_overrides"]["model.language_model.layers.0.router.proj.weight:0"]={"bits":4,"group_size":32,"clip_ratio":1}
        with self.assertRaises(ContractError):validate_quant_plan(bad,index["weight_map"])
        name=plan["expert_tensors"][0]
        array=np.ones((128,2,32),np.float32)
        self.assertEqual(len(quantize_expert_tensor(array,name,plan)),128)

    def test_bf16_passthrough_and_quantization(self):
        source=float_to_bf16(np.array([[0.0,1.0,-2.0,3.25]*8],np.float32))
        self.assertTrue(np.array_equal(source,dequantize(quantize(source,16,32))))
        q=dequantize(quantize(source,4,32))
        self.assertEqual(q.dtype,np.uint16);self.assertEqual(q.shape,source.shape)
        self.assertTrue(np.isfinite(bf16_to_float(q)).all())

    def test_exact_tensor_selection(self):
        names=[f"model.language_model.layers.{i}.experts.{kind}" for i in range(30) for kind in ("gate_up_proj","down_proj")]
        self.assertEqual(len(select_expert_tensors(names+["model.language_model.layers.0.router.scale"])),60)
        with self.assertRaises(ContractError):select_expert_tensors(names[:-1])

    def test_prune_ids_and_router_scales(self):
        source={"experts.gate_up_proj":np.arange(128*4*3,dtype=np.float32).reshape(128,4,3),
                "experts.down_proj":np.arange(128*3*4,dtype=np.float32).reshape(128,3,4),
                "router.proj.weight":np.ones((128,4),np.float32),
                "router.per_expert_scale":np.arange(128,dtype=np.float32),
                "router.scale":np.array([0.25],np.float32)}
        keep=list(range(0,128,2))
        cand=construct_pruned_layer(source,keep)
        self.assertTrue(admit_pruned_layer(source,cand,keep))
        cand["router.proj.weight"]+=0.1
        self.assertTrue(admit_pruned_layer(source,cand,keep))
        for key in ("router.scale","router.per_expert_scale"):
            bad=copy.deepcopy(cand);bad[key].flat[0]+=1
            with self.assertRaises(ContractError):admit_pruned_layer(source,bad,keep)
        plan=frequency_map({str(i):[1]*128 for i in range(30)})
        self.assertEqual(plan["layers"]["0"],list(range(96)))
        self.assertEqual(validate_expert_map(plan),2880)
        plan["layers"]["0"][1]=0
        with self.assertRaises(ContractError):validate_expert_map(plan)

    def test_declared_low_rank_recovery(self):
        source={"experts.gate_up_proj":np.zeros((128,4,3),np.float32),
                "experts.down_proj":np.zeros((128,3,4),np.float32),
                "router.proj.weight":np.ones((128,4),np.float32),
                "router.per_expert_scale":np.ones(128,np.float32),
                "router.scale":np.ones(1,np.float32)}
        keep=list(range(96));cand=construct_pruned_layer(source,keep)
        a=np.ones((4,1),np.float32);b=np.ones((1,3),np.float32)
        cand["experts.gate_up_proj"][0]=a@b
        with self.assertRaises(ContractError):admit_pruned_layer(source,cand,keep)
        self.assertTrue(admit_pruned_layer(source,cand,keep,{"experts.gate_up_proj":{0:{"a":a,"b":b}}}))

    def test_b0_materializer_verifies_existing_snapshot_without_model_compute(self):
        import hashlib
        import importlib.util
        import json
        module_spec=importlib.util.spec_from_file_location("b0_materializer",ROOT/"solution/materialize_baseline.py")
        module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            temporary=Path(temporary);snapshot=temporary/"cache/snapshots"/SOURCE_REVISION
            blobs=temporary/"cache/blobs";snapshot.mkdir(parents=True);blobs.mkdir()
            # Deliberately tiny fixture: validates file-copy and hash contracts,
            # never a GEV checkpoint or an evidence artifact for publication.
            header=json.dumps({"example":{"dtype":"BF16","shape":[1],"data_offsets":[0,2]}}).encode()
            shard=len(header).to_bytes(8,"little")+header+b"\x00\x00"
            index={"metadata":{"total_size":2},"weight_map":{"example":"model-00001.safetensors"}}
            payloads={name:b"{}" for name in ("config.json","tokenizer.json","tokenizer_config.json","processor_config.json","head.safetensors","calibration.json","calibration_gold.json","judge_config.json","adapter/adapter_model.safetensors")}
            payloads.update({"chat_template.jinja":b"template","model.safetensors.index.json":json.dumps(index).encode(),"model-00001.safetensors":shard})
            for name,data in payloads.items():
                blob=blobs/hashlib.sha256(data).hexdigest();blob.write_bytes(data)
                path=snapshot/name;path.parent.mkdir(parents=True,exist_ok=True);path.symlink_to(blob)
            metadata=temporary/"fixture/source";metadata.mkdir(parents=True)
            (metadata/"metadata-receipts.json").write_text(json.dumps({"files":{name:{"sha256":hashlib.sha256(payloads[name]).hexdigest()} for name in ("config.json","model.safetensors.index.json")}}))
            module.ROOT=temporary/"fixture"
            output=module.materialize(snapshot,temporary/"output")
            receipt=json.loads((output/"prepared-artifact.json").read_text())
            self.assertEqual(receipt["baseline_id"],"B0")
            self.assertFalse(receipt["model_computation_performed"])
            self.assertFalse(receipt["measurements_available"])
            self.assertFalse((output/"model-00001.safetensors").is_symlink())
            self.assertFalse(receipt["upstream_inventory_verified"])
            inventory={"schema":"upstream-blob-inventory-v1","repo_id":module.REPO_ID,"revision":SOURCE_REVISION,"files":{name:{"content_address":hashlib.sha256(data).hexdigest(),"bytes":len(data)} for name,data in payloads.items()}}
            inventory_path=temporary/"inventory.json";inventory_path.write_text(json.dumps(inventory))
            checked=module.materialize(snapshot,temporary/"inventory-checked-output",inventory_path)
            self.assertTrue(json.loads((checked/"prepared-artifact.json").read_text())["upstream_inventory_verified"])
            inventory["files"]["head.safetensors"]["content_address"]="0"*64
            inventory_path.write_text(json.dumps(inventory))
            with self.assertRaisesRegex(ValueError,"exact upstream revision member"):
                module.materialize(snapshot,temporary/"wrong-member-output",inventory_path)
            # Hash corruption cannot create a materialized baseline.
            (snapshot/"model-00001.safetensors").resolve().write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError,"content hash mismatch"):
                module.materialize(snapshot,temporary/"corrupt-output")
            self.assertFalse((temporary/"corrupt-output").exists())

    def fixtures(self):
        # Deliberately synthetic arithmetic fixtures. Never written as reference caches.
        ref={"schema":"reference-cache-v1","status":"measured","source_revision":SOURCE_REVISION,
             "B0":{"accuracy":1.0,"family_accuracy":{f:1.0 for f in FAMILIES},"brier":0,"model_bytes":1000,"latency_seconds":10}}
        metrics={"accuracy":1.0,"family_accuracy":{f:1.0 for f in FAMILIES},"brier":0,"count":576}
        resources={"status":"complete","model_bytes":400,"peak_gpu_bytes":1024,"latency_pass_seconds":[10,10,10],"judge_wall_seconds":30,"artifact_admission":"passed"}
        return ref,metrics,resources

    def test_score_full_marks_quality_zero_missing_reference(self):
        ref,metrics,res=self.fixtures()
        self.assertEqual(compose("quant",metrics,res,ref,0.05)["score"],100)
        self.assertEqual(compose("quant",metrics,res,ref,0.1)["score"],100)
        res["model_bytes"]=700
        self.assertAlmostEqual(compose("quant",metrics,res,ref,0.1)["score"],50)
        res["model_bytes"]=1000
        self.assertEqual(compose("quant",metrics,res,ref,0.0)["score"],0)
        res["model_bytes"]=400
        # Optional control measurements must not affect score or latency gates.
        altered=copy.deepcopy(ref);altered["BQ"]={"distortion":0,"latency_seconds":0.001}
        self.assertEqual(compose("quant",metrics,res,altered,0.1)["score"],100)
        plan=frequency_map({str(i):[1]*128 for i in range(30)})
        self.assertAlmostEqual(compose("prune",metrics,res,ref,expert_map=plan)["score"],100*2/3)
        full={**plan,"layers":{str(i):list(range(80)) for i in range(30)}}
        self.assertEqual(compose("prune",metrics,res,ref,expert_map=full)["score"],100)
        intact={**plan,"layers":{str(i):list(range(128)) for i in range(30)}}
        self.assertEqual(compose("prune",metrics,res,ref,expert_map=intact)["score"],0)
        metrics["brier"]=0.02
        self.assertEqual(compose("quant",metrics,res,ref,0.0)["score"],0)
        with self.assertRaises(ContractError):validate_reference(read_json(ROOT/"public-authoring/reference_cache.json"),"quant")
        res["judge_wall_seconds"]=3601
        with self.assertRaises(ContractError):compose("quant",metrics,res,ref,0.0)

    def test_tv_and_budget(self):
        self.assertAlmostEqual(total_variation(np.array([0.7,0.3],np.float32),np.array([0.6,0.4],np.float32)),0.1,places=6)
        with self.assertRaises(ContractError):total_variation(np.array([2,0],np.float32),np.array([1,0],np.float32))
        event={"event_id":"teacher","kind":"inference","input_tokens":300000,"output_tokens":200001,"seconds":1,"optimizer_updates":0}
        with self.assertRaises(ContractError):validate_ledger([event],"prune")
        event["output_tokens"]=200000
        self.assertEqual(validate_ledger([event],"prune")["inference_tokens"],500000)
        with self.assertRaises(ContractError):validate_ledger([event,event],"prune")

if __name__=="__main__":
    unittest.main()
