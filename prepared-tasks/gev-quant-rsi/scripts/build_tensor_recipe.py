"""Build a declarative CPU tensor-selection recipe from pinned source metadata."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from taskkit.common import read_json,write_json
from taskkit.tensors import make_quant_plan,validate_quant_plan
root=Path(__file__).resolve().parents[1]
index=read_json(root/"source/metadata/model.safetensors.index.json")
plan=make_quant_plan(index["weight_map"])
validate_quant_plan(plan,index["weight_map"])
write_json(root/"configs/tensor_selection.json",plan)
print("60 fused source expert tensors selected; recipe only, no quantized checkpoint created.")

