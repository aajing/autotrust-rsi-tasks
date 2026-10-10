"""CPU-only public-package validation; no model downloads or inference."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from taskkit.common import file_hash,read_json,read_jsonl,write_json
from taskkit.data import audit,build

def main():
    start=time.monotonic();logs=[]
    def run(args,expected=0):
        result=subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)
        logs.append("$ python "+" ".join(args)+"\n"+result.stdout+result.stderr)
        if result.returncode!=expected:
            raise RuntimeError("unexpected process status: "+str(result.returncode)+"\n"+logs[-1])
        return result
    run(["-m","unittest","discover","-s","tests","-v"])
    cfg=read_json(ROOT/"task.json")
    before=file_hash(ROOT/"data/manifest.json");build(ROOT)
    assert file_hash(ROOT/"data/manifest.json")==before,"non-deterministic rebuild"
    assert audit(ROOT)["status"]=="pass"
    assert not (ROOT/"authoring").exists(),"obsolete nonpublic asset directory"
    staged_count=0
    with tempfile.TemporaryDirectory(prefix=cfg["slug"]+"-cpu-") as tmp:
        tmp=Path(tmp);staged=tmp/"work"
        run(["scripts/stage_work.py",str(staged)])
        work=read_json(staged/"work_manifest.json")
        assert work["benchmark_visibility"]=="public" and work["evaluation_assets_included"]
        for name in ("data/public/evaluation.inputs.jsonl","data/public/evaluation.gold.jsonl","public-authoring/evaluation_seed.json","public-authoring/reference_cache.json"):
            assert file_hash(staged/name)==file_hash(ROOT/name)
        staged_count=len(work["files"])
        gold=read_jsonl(ROOT/"data/public/evaluation.gold.jsonl")
        predictions=tmp/"fixture-predictions.jsonl"
        predictions.write_text("".join(json.dumps({"id":g["id"],"output":g["canonical_output"]})+"\n" for g in gold))
        public=run(["-m","taskkit.cli","public-assess","--split","evaluation","--predictions",str(predictions)])
        assert json.loads(public.stdout)["metrics"]["accuracy"]==1
        missing=run(["-m","taskkit.cli","assess","--predictions",str(predictions),"--resources",str(tmp/"absent-resources.json"),"--references","public-authoring/reference_cache.json"],2)
        missing_result=json.loads(missing.stdout)
        assert missing_result["status"]=="unscored"
        run(["solution/materialize_baseline.py","--source-snapshot",str(tmp/"absent-baseline"),"--output",str(tmp/"candidate")],1)
        run(["scripts/gpu_entrypoint.py"],1)
    fields=[tuple(part.strip() for part in line.split("|")[1:3]) for line in (ROOT/"proposal.md").read_text().splitlines() if line.startswith("| ")][2:]
    assert len(fields)==28 and len(set(fields))==28
    write_json(ROOT/"cpu-validation.json",{"schema":"cpu-validation-v2","scope":"CPU data/oracle/arithmetic contracts only; fixtures are not model scores","benchmark_visibility":"public","dataset_counts":cfg["counts"],"data_manifest_sha256":before,"test_count":16,"test_status":"passed","gold_oracle_cases_checked":sum(cfg["counts"].values()),"deterministic_rebuild":"passed","work_public_evaluation_included":"passed","staged_file_count":staged_count,"missing_reference_assessment":missing_result,"missing_baseline_materializer":"refused","gpu_entrypoint":"refused-unimplemented","model_weights_downloaded":False,"gpu_runs":0,"python":platform.python_version(),"numpy":np.__version__,"elapsed_cpu_check_seconds":round(time.monotonic()-start,3)})
    (ROOT/"cpu-checks.log").write_text("CPU-only validation. Golden-answer fixtures are not model results.\n\n"+"\n".join(logs))
    print(json.dumps({"status":"passed","slug":cfg["slug"],"tests":16,"public_cases":sum(cfg["counts"].values()),"data_manifest_sha256":before},indent=2))

if __name__=="__main__":main()
