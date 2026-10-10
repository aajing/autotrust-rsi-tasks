"""Strict CPU assessment over captured outputs; not a GPU inference harness."""
import math
import statistics
from pathlib import Path
import numpy as np
from .common import FAMILIES,ContractError,SOURCE_REVISION,exact_coverage,finite_number,file_hash,paths,read_json,read_jsonl
from .oracles import evaluate_answer
from .tensors import validate_expert_map

def aggregate(inputs,gold,predictions):
    ids=[r["id"] for r in inputs]
    if len(set(ids))!=len(ids):
        raise ContractError("duplicate input IDs")
    g=exact_coverage(gold,ids,"gold");p=exact_coverage(predictions,ids,"predictions")
    correct={f:[] for f in FAMILIES};brier=[]
    for row in inputs:
        if row["family"] not in correct or g[row["id"]]["family"]!=row["family"]:
            raise ContractError("family mismatch")
        prediction=p[row["id"]]
        if set(prediction)!={"id","output"}:
            raise ContractError("prediction schema mismatch")
        result=evaluate_answer(g[row["id"]],prediction["output"])
        correct[row["family"]].append(int(result["correct"]))
        if row["family"]=="confidence":
            brier.append(result["brier"])
    if any(not v for v in correct.values()) or len(set(map(len,correct.values())))!=1:
        raise ContractError("incomplete/unbalanced family coverage")
    per_family={f:sum(v)/len(v) for f,v in correct.items()}
    return {"family_accuracy":per_family,"accuracy":sum(per_family.values())/6,"brier":sum(brier)/len(brier),"count":len(ids)}

def validate_reference(ref,mode):
    if not isinstance(ref,dict) or ref.get("schema")!="reference-cache-v1" or ref.get("status")!="measured" or ref.get("source_revision")!=SOURCE_REVISION:
        raise ContractError("reference cache is unmaterialized or incompatible")
    b0=ref.get("B0")
    if not isinstance(b0,dict):
        raise ContractError("B0 reference missing")
    for key in ("accuracy","brier"):
        finite_number(b0.get(key),"B0."+key,0,1)
    if set(b0.get("family_accuracy",{}))!=set(FAMILIES):
        raise ContractError("B0 family references missing")
    for v in b0["family_accuracy"].values():finite_number(v,"family accuracy",0,1)
    if abs(sum(b0["family_accuracy"].values())/6-b0["accuracy"])>1e-12:
        raise ContractError("B0 macro mismatch")
    finite_number(b0.get("model_bytes"),"B0.model_bytes",1)
    finite_number(b0.get("latency_seconds"),"B0.latency",0.000001)
    return ref

def compose(mode,metrics,resources,ref,distortion=None,expert_map=None):
    validate_reference(ref,mode)
    required={"status","model_bytes","peak_gpu_bytes","latency_pass_seconds","judge_wall_seconds","artifact_admission"}
    if set(resources)!=required or resources["status"]!="complete" or resources["artifact_admission"]!="passed":
        raise ContractError("incomplete resources or artifact admission")
    if finite_number(resources["judge_wall_seconds"],"Judge wall seconds",0)>3600:
        raise ContractError("Judge timeout")
    byte_count=finite_number(resources["model_bytes"],"model bytes",1)
    memory=finite_number(resources["peak_gpu_bytes"],"peak bytes",1)
    timings=resources["latency_pass_seconds"]
    if not isinstance(timings,list) or len(timings)!=3:
        raise ContractError("three timing passes required")
    latency=statistics.median(finite_number(v,"latency",0.000001) for v in timings)
    b0=ref["B0"]
    gates={"macro_quality":metrics["accuracy"]+1e-12>=b0["accuracy"]-0.01,
           "family_quality":all(metrics["family_accuracy"][f]+1e-12>=b0["family_accuracy"][f]-0.03 for f in FAMILIES),
           "calibration":metrics["brier"]<=b0["brier"]+0.01+1e-12,
           "storage":byte_count<=b0["model_bytes"]*(1.0 if mode=="quant" else 0.85),
           "peak_memory":memory<=64*(1024**3),
           "latency":latency<=b0["latency_seconds"]*1.10}
    if mode=="quant":
        d=finite_number(distortion,"candidate distortion",0,1)
        raw=100*max(0,min(1,(1-byte_count/b0["model_bytes"])/0.60))
    elif mode=="prune":
        retained=validate_expert_map(expert_map)
        raw=100*max(0,min(1,(3840-retained)/1440))
    else:
        raise ContractError("unknown task mode")
    return {"status":"scored_assessment","official_reward":False,"score":raw if all(gates.values()) else 0.0,"gates":gates,"metrics":metrics,"latency_seconds":latency,"distortion_vs_B0":distortion,"storage_ratio_vs_B0":byte_count/b0["model_bytes"]}

def total_variation(p,q):
    p=np.asarray(p);q=np.asarray(q)
    if p.dtype!=np.float32 or q.dtype!=np.float32 or p.ndim!=1 or p.shape!=q.shape or not np.isfinite(p).all() or not np.isfinite(q).all() or np.any(p<0) or np.any(q<0):
        raise ContractError("invalid probability vectors")
    if abs(float(p.sum(dtype=np.float64))-1)>1e-5 or abs(float(q.sum(dtype=np.float64))-1)>1e-5:
        raise ContractError("probabilities do not sum to one")
    return float(np.abs(p.astype(np.float64)-q.astype(np.float64)).sum()/2)

def assess(root,predictions,resources,ref_path,probe_dir=None,expert_map=None):
    root=Path(root);cfg=read_json(root/"task.json");ref=read_json(ref_path)
    validate_reference(ref,cfg["mode"])
    if ref.get("dataset_manifest_sha256")!=file_hash(root/"data/manifest.json"):
        raise ContractError("reference dataset binding mismatch")
    # Real source/preparation evidence is not constructed by this CPU-only package.
    if not ref.get("runtime_fingerprint") or not ref.get("source_inventory_sha256"):
        raise ContractError("measured runtime/source evidence missing")
    ip,gp=paths(root,"evaluation")
    metrics=aggregate(read_jsonl(ip),read_jsonl(gp),read_jsonl(predictions))
    distortion=None
    if cfg["mode"]=="quant":
        plan=read_json(root/"public-authoring/probe_plan.json")
        if not plan.get("positions_materialized") or not probe_dir:
            raise ContractError("pinned-tokenizer probes not materialized")
        by_id=ref["B0"].get("probe_vectors",{})
        if set(by_id)!=set(plan["ids"]):
            raise ContractError("reference probe coverage mismatch")
        candidate=Path(probe_dir)
        if set(p.stem for p in candidate.glob("*.npy"))!={str(i) for i in range(80)}:
            raise ContractError("candidate probe coverage mismatch")
        ds=[]
        for i,record_id in enumerate(plan["ids"]):
            rel=by_id[record_id]["path"];p=(root/rel).resolve()
            if not p.is_relative_to((root/"public-authoring").resolve()) or file_hash(p)!=by_id[record_id]["sha256"]:
                raise ContractError("untrusted reference vector path/hash")
            a=np.load(p,allow_pickle=False);b=np.load(candidate/f"{i}.npy",allow_pickle=False)
            if a.shape!=(262144,) or b.shape!=(262144,):
                raise ContractError("wrong probe vocabulary")
            ds.append(total_variation(a,b))
        distortion=sum(ds)/len(ds)
    return compose(cfg["mode"],metrics,read_json(resources),ref,distortion,read_json(expert_map) if expert_map else None)
