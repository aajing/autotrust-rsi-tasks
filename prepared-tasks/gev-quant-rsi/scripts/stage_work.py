"""Stage this public benchmark, including evaluation inputs, gold, seeds and probes."""
import argparse
import shutil
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from taskkit.common import ContractError,file_hash,write_json
p=argparse.ArgumentParser();p.add_argument("destination");args=p.parse_args()
root=Path(__file__).resolve().parents[1];dest=Path(args.destination).resolve()
if dest.exists() or dest.is_relative_to(root) or root.is_relative_to(dest):
    raise SystemExit("Use a new destination outside the source package.")
dest.mkdir(parents=True)
for name in ("taskkit","data","public-authoring","configs","solution","source","scripts","tests","task.json","requirements.txt","requirements-cpu.lock.txt","README.md","RUNBOOK.md","INTEGRATION.md","CONTRIBUTOR.md","LICENSES.md","proposal.md"):
    src=root/name
    if src.is_dir():
        shutil.copytree(src,dest/name,ignore=shutil.ignore_patterns("__pycache__","*.pyc","downloaded-model"))
    elif src.is_file():
        (dest/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/name)
required=("data/public/evaluation.inputs.jsonl","data/public/evaluation.gold.jsonl","public-authoring/evaluation_seed.json","public-authoring/probe_plan.json","public-authoring/reference_cache.json")
if any(not (dest/name).is_file() for name in required):
    raise ContractError("public evaluation release is incomplete")
write_json(dest/"work_manifest.json",{"benchmark_visibility":"public","evaluation_assets_included":True,"protocol":"fit practice only; development selects; evaluation is inspectable and not a secret generalization test","files":{str(f.relative_to(dest)):file_hash(f) for f in dest.rglob("*") if f.is_file()}})
print(dest)
