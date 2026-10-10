"""CPU reference arithmetic; these routines are not H100 kernels."""
import math
import re
import numpy as np
from .common import ContractError,SOURCE_REVISION

EXPERT_PATTERN=re.compile(r"^model\.language_model\.layers\.(\d+)\.experts\.(gate_up_proj|down_proj)$")

def bf16_to_float(bits):
    bits=np.asarray(bits)
    if bits.dtype!=np.uint16:
        raise ContractError("BF16 storage must use uint16 words")
    return (bits.astype(np.uint32)<<16).view(np.float32)

def float_to_bf16(values):
    values=np.asarray(values)
    if values.dtype!=np.float32 or not np.isfinite(values).all():
        raise ContractError("finite float32 values required")
    bits=values.view(np.uint32)
    rounded=bits+np.uint32(0x7fff)+((bits>>16)&1)
    out=(rounded>>16).astype(np.uint16)
    if not np.isfinite(bf16_to_float(out)).all():
        raise ContractError("BF16 overflow")
    return out

def quantize(source,bits=4,group_size=128,clip_ratio=1.0):
    source=np.asarray(source)
    if source.ndim<2 or any(n<=0 for n in source.shape):
        raise ContractError("nonempty matrix/tensor required")
    if source.dtype==np.uint16:
        original_dtype="bfloat16";values=bf16_to_float(source)
    elif source.dtype==np.float32:
        original_dtype="float32";values=source
    else:
        raise ContractError("only float32 CPU reference or uint16 BF16 source accepted")
    if not np.isfinite(values).all():
        raise ContractError("nonfinite weights")
    if bits not in (4,8,16) or group_size not in (32,64,128):
        raise ContractError("unsupported format")
    if not isinstance(clip_ratio,(int,float)) or not math.isfinite(clip_ratio) or not 0<clip_ratio<=1:
        raise ContractError("clip ratio must be in (0,1]")
    meta={"schema":"cpu-quant-v1","bits":bits,"group_size":group_size,"shape":list(source.shape),"source_dtype":original_dtype,"rounding":"nearest_ties_even","clip_ratio":float(clip_ratio)}
    if bits==16:
        if original_dtype!="bfloat16":
            raise ContractError("16-bit route requires BF16 source")
        return {"meta":meta,"values":source.copy(),"scales":np.empty((0,),np.float32)}
    qmax=(1<<(bits-1))-1
    padded=((source.shape[-1]+group_size-1)//group_size)*group_size
    work=np.zeros((*source.shape[:-1],padded),dtype=np.float32)
    work[...,:source.shape[-1]]=values
    blocks=work.reshape(-1,group_size)
    amax=np.max(np.abs(blocks),axis=1)*np.float32(clip_ratio)
    scales=np.where(amax==0,np.float32(1),amax/np.float32(qmax)).astype(np.float32)
    ints=np.clip(np.rint(blocks/scales[:,None]),-qmax,qmax).astype(np.int8).reshape(-1)
    if bits==4:
        unsigned=(ints.astype(np.int16)&15).astype(np.uint8)
        packed=unsigned[::2]|(unsigned[1::2]<<4)
    else:
        packed=ints
    meta["padded_last_dim"]=padded
    return {"meta":meta,"values":packed,"scales":scales}

def dequantize(package):
    meta=package["meta"];values=np.asarray(package["values"]);scales=np.asarray(package["scales"])
    if set(meta)-{"schema","bits","group_size","shape","source_dtype","rounding","clip_ratio","padded_last_dim"}:
        raise ContractError("unknown quantization field")
    if meta.get("schema")!="cpu-quant-v1" or meta.get("rounding")!="nearest_ties_even":
        raise ContractError("unsupported quantization metadata")
    shape=meta["shape"];bits=meta["bits"];group=meta["group_size"]
    if len(shape)<2 or any(type(n)!=int or n<=0 for n in shape) or bits not in (4,8,16) or group not in (32,64,128):
        raise ContractError("invalid dimensions/format")
    if meta["source_dtype"] not in ("float32","bfloat16"):
        raise ContractError("invalid source dtype")
    if bits==16:
        if meta["source_dtype"]!="bfloat16" or values.dtype!=np.uint16 or list(values.shape)!=shape or scales.dtype!=np.float32 or scales.shape!=(0,):
            raise ContractError("invalid BF16 passthrough")
        if not np.isfinite(bf16_to_float(values)).all():
            raise ContractError("nonfinite BF16")
        return values.copy()
    padded=((shape[-1]+group-1)//group)*group
    total=math.prod(shape[:-1])*padded
    if meta.get("padded_last_dim")!=padded or scales.dtype!=np.float32 or scales.shape!=(total//group,) or not np.isfinite(scales).all() or np.any(scales<=0):
        raise ContractError("invalid scales or padding")
    if bits==4:
        if values.dtype!=np.uint8 or values.shape!=(total//2,):
            raise ContractError("invalid packed INT4 shape/dtype")
        nibbles=np.empty(total,np.int8);nibbles[::2]=values&15;nibbles[1::2]=(values>>4)&15
        ints=np.where(nibbles>=8,nibbles.astype(np.int16)-16,nibbles).astype(np.int8)
        if np.any(ints==-8):
            raise ContractError("reserved -8 code in symmetric INT4")
    else:
        if values.dtype!=np.int8 or values.shape!=(total,) or np.any(values==-128):
            raise ContractError("invalid symmetric INT8 payload")
        ints=values
    arr=(ints.reshape(-1,group).astype(np.float32)*scales[:,None]).reshape(*shape[:-1],padded)[...,:shape[-1]].copy()
    return float_to_bf16(arr) if meta["source_dtype"]=="bfloat16" else arr

def select_expert_tensors(names):
    selected=[]
    for name in names:
        match=EXPERT_PATTERN.fullmatch(name)
        if match:
            if not 0<=int(match.group(1))<30:
                raise ContractError("layer index outside fixed source")
            selected.append(name)
    expected={f"model.language_model.layers.{i}.experts.{kind}" for i in range(30) for kind in ("gate_up_proj","down_proj")}
    if set(selected)!=expected:
        raise ContractError("source index must contain exactly 60 fused expert tensors")
    return sorted(selected)

def validate_expert_map(plan,layers=30,experts=128,minimum=64):
    if set(plan)!={"schema","source_revision","top_k","layers"} or plan["schema"]!="expert-map-v1" or plan["source_revision"]!=SOURCE_REVISION or plan["top_k"]!=8:
        raise ContractError("invalid expert map header")
    if set(plan["layers"])!={str(i) for i in range(layers)}:
        raise ContractError("expert map requires every layer")
    for ids in plan["layers"].values():
        if not isinstance(ids,list) or not minimum<=len(ids)<=experts or any(type(i)!=int or not 0<=i<experts for i in ids) or len(set(ids))!=len(ids) or ids!=sorted(ids):
            raise ContractError("retained IDs must be sorted, unique and within per-layer bounds")
    return sum(len(x) for x in plan["layers"].values())

def frequency_map(counts):
    if set(counts)!={str(i) for i in range(30)}:
        raise ContractError("missing routing-count layer")
    layers={}
    for layer,values in counts.items():
        if len(values)!=128 or any(type(v)!=int or v<0 for v in values):
            raise ContractError("routing counts require 128 nonnegative integers")
        layers[layer]=sorted(sorted(range(128),key=lambda i:(-values[i],i))[:96])
    return {"schema":"expert-map-v1","source_revision":SOURCE_REVISION,"top_k":8,"layers":layers}

LAYER_KEYS={"experts.gate_up_proj","experts.down_proj","router.proj.weight","router.per_expert_scale","router.scale"}

def construct_pruned_layer(source,keep):
    if set(source)!=LAYER_KEYS or not isinstance(keep,list) or len(set(keep))!=len(keep) or not 8<=len(keep)<=128 or keep!=sorted(keep) or any(type(i)!=int or not 0<=i<128 for i in keep):
        raise ContractError("invalid source layer or kept IDs")
    source={k:np.asarray(v) for k,v in source.items()}
    for name,arr in source.items():
        if name!="router.scale" and (arr.ndim<1 or arr.shape[0]!=128):
            raise ContractError("expert/router first dimension must be 128")
    return {k:(v.copy() if k=="router.scale" else v[keep].copy()) for k,v in source.items()}

def admit_pruned_layer(source,candidate,keep,expert_recovery=None):
    if expert_recovery is not None and (not isinstance(expert_recovery,dict) or set(expert_recovery)-{"experts.gate_up_proj","experts.down_proj"}):
        raise ContractError("recovery factors outside declared expert tensors")
    expected=construct_pruned_layer(source,keep)
    if set(candidate)!=LAYER_KEYS:
        raise ContractError("unknown/missing tensor")
    for key,ref in expected.items():
        arr=np.asarray(candidate[key])
        if arr.dtype!=ref.dtype or arr.shape!=ref.shape:
            raise ContractError("candidate tensor dtype/shape mismatch")
        if arr.dtype==np.uint16:
            if not np.isfinite(bf16_to_float(arr)).all():
                raise ContractError("nonfinite BF16 payload")
        elif not np.isfinite(arr).all():
            raise ContractError("nonfinite tensor")
        if key=="router.proj.weight":
            continue
        if key.startswith("experts.") and expert_recovery and key in expert_recovery:
            recovered=ref.copy()
            for slot,entry in expert_recovery[key].items():
                if type(slot)!=int or not 0<=slot<len(keep) or set(entry)!={"a","b"}:
                    raise ContractError("invalid recovery factor slot")
                a=np.asarray(entry["a"]);b=np.asarray(entry["b"])
                if a.dtype!=np.float32 or b.dtype!=np.float32 or a.ndim!=2 or b.ndim!=2 or not 1<=a.shape[1]<=16 or a.shape[1]!=b.shape[0] or a.shape[0]!=ref[slot].shape[0] or b.shape[1]!=ref[slot].shape[1] or not np.isfinite(a).all() or not np.isfinite(b).all():
                    raise ContractError("invalid rank<=16 recovery factors")
                base=bf16_to_float(ref[slot]) if ref.dtype==np.uint16 else ref[slot]
                value=(base+a@b).astype(np.float32)
                recovered[slot]=float_to_bf16(value) if ref.dtype==np.uint16 else value
            ref=recovered
        if not np.array_equal(arr,ref):
            raise ContractError("frozen tensor or declared recovery mismatch: "+key)
    return True

def make_quant_plan(source_names):
    selected=select_expert_tensors(source_names)
    return {"schema":"quant-recipe-v1","source_revision":SOURCE_REVISION,"status":"recipe-only",
            "expert_tensors":selected,"default_bits":4,"default_group_size":128,
            "default_clip_ratio":1.0,"per_expert_overrides":{},"frozen_policy":"bitwise_source_copy"}

def validate_quant_plan(plan,source_names):
    fields={"schema","source_revision","status","expert_tensors","default_bits","default_group_size","default_clip_ratio","per_expert_overrides","frozen_policy"}
    if set(plan)!=fields or plan["schema"]!="quant-recipe-v1" or plan["source_revision"]!=SOURCE_REVISION or plan["status"]!="recipe-only" or plan["frozen_policy"]!="bitwise_source_copy":
        raise ContractError("invalid quantization recipe")
    expected=select_expert_tensors(source_names)
    if plan["expert_tensors"]!=expected:
        raise ContractError("quantization tensor allowlist mismatch")
    def check_format(x):
        if type(x["bits"])!=int or x["bits"] not in (4,8,16) or type(x["group_size"])!=int or x["group_size"] not in (32,64,128) or isinstance(x["clip_ratio"],bool) or not isinstance(x["clip_ratio"],(int,float)) or not math.isfinite(x["clip_ratio"]) or not 0<x["clip_ratio"]<=1:
            raise ContractError("invalid expert quantization format")
    check_format({"bits":plan["default_bits"],"group_size":plan["default_group_size"],"clip_ratio":plan["default_clip_ratio"]})
    if not isinstance(plan["per_expert_overrides"],dict):
        raise ContractError("overrides must be a map")
    for name,entry in plan["per_expert_overrides"].items():
        tensor,sep,expert=name.rpartition(":")
        if not sep or tensor not in expected or not expert.isdecimal() or str(int(expert))!=expert or not 0<=int(expert)<128:
            raise ContractError("override outside source experts")
        if set(entry)!={"bits","group_size","clip_ratio"}:
            raise ContractError("unknown override field")
        check_format(entry)
    return True

def quantize_expert_tensor(source,tensor_name,plan):
    if tensor_name not in plan["expert_tensors"]:
        raise ContractError("tensor is outside the expert allowlist")
    source=np.asarray(source)
    if source.ndim!=3 or source.shape[0]!=128:
        raise ContractError("fused source expert tensor must have first dimension 128")
    output=[]
    for i in range(128):
        fmt=plan["per_expert_overrides"].get(tensor_name+":"+str(i),
            {"bits":plan["default_bits"],"group_size":plan["default_group_size"],"clip_ratio":plan["default_clip_ratio"]})
        output.append(quantize(source[i],fmt["bits"],fmt["group_size"],fmt["clip_ratio"]))
    return output

def iter_pruned_checkpoint(source_tensors,plan):
    """Yield frozen tensors or structurally sliced tensors; no model class is instantiated."""
    validate_expert_map(plan)
    consumed=set()
    for layer,keep in plan["layers"].items():
        prefix=f"model.language_model.layers.{layer}."
        source={key:source_tensors[prefix+key] for key in LAYER_KEYS}
        pruned=construct_pruned_layer(source,keep)
        for key,value in pruned.items():
            consumed.add(prefix+key);yield prefix+key,value
    for key,value in source_tensors.items():
        if key not in consumed:
            yield key,value
