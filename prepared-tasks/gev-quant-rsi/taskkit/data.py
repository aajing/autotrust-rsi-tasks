import hashlib
import random
import secrets
from collections import Counter
from fractions import Fraction
from pathlib import Path
from .common import FAMILIES,ContractError,canonical,digest,file_hash,paths,read_json,read_jsonl,write_json,write_jsonl
from .oracles import sql_result
from .render import render

def make(family,difficulty,rng,target_label):
    hard=difficulty=="compositional"
    if family=="math":
        q,p,fee=rng.randint(2,40),rng.randint(3,99),rng.randint(1,35)
        discount,tax=rng.choice([0,5,10,15,20]),rng.choice([5,8,10,12])
        params={"quantity":q,"price":p,"fee":fee,"discount":discount,"tax":tax if hard else 0}
        total=Fraction(q*p*(100-discount),100)+fee
        if hard: total*=Fraction(100+tax,100)
        prompt=f"Buy {q} items at {p} units each. Discount the item subtotal by {discount}%, then add a fixed fee of {fee} units."
        if hard:prompt+=f" Apply {tax}% tax to the resulting total."
        prompt+=" Return only the exact total as an integer or reduced fraction p/q."
        return params,prompt,{"answer":str(total),"canonical_output":str(total)}
    if family=="python":
        a,b,m=rng.randint(1,9),rng.randint(-20,20),rng.randint(2,13);rem=rng.randrange(m);bound=rng.randint(-25,25)
        params={"a":a,"b":b,"mod":m,"remainder":rem,"bound":bound if hard else None}
        condition=f"x % {m} == {rem}"+(f" and x >= {bound}" if hard else "")
        code=f"def solve(xs):\n    return sum(x * {a} + ({b}) for x in xs if {condition})"
        prompt=f"Write Python function solve(xs) returning the sum of x*{a}+({b}) for integers x in xs satisfying x % {m} == {rem}."
        if hard:prompt+=f" Also require x >= {bound}."
        prompt+=" Output only a function with one return expression; sum and a generator expression are allowed. No imports."
        tests=[]
        for _ in range(12):
            xs=[rng.randint(-50,50) for _ in range(rng.randint(0,12))]
            val=sum(x*a+b for x in xs if x%m==rem and (not hard or x>=bound))
            tests.append({"input":xs,"output":val})
        return params,prompt,{"tests":tests,"canonical_output":code}
    if family=="sql":
        lo,hi=rng.randint(1,12),rng.randint(15,29);minimum=rng.randint(0,100)
        params={"schema":"orders(id,region,amount,quantity,fee,day,active)","lo":lo,"hi":hi,"minimum":minimum,"group":hard}
        if hard:
            query=f"SELECT region, SUM(amount * quantity + fee) FROM orders WHERE active=1 AND day BETWEEN {lo} AND {hi} GROUP BY region HAVING SUM(amount * quantity + fee)>={minimum} ORDER BY region"
            prompt=f"Return region and SUM(amount*quantity+fee) for active=1 rows with day between {lo} and {hi}, inclusive. Group by region, keep totals >= {minimum}, order by region."
        else:
            query=f"SELECT COALESCE(SUM(amount * quantity + fee),0) FROM orders WHERE active=1 AND day BETWEEN {lo} AND {hi} AND amount>={minimum}"
            prompt=f"Return one value: SUM(amount*quantity+fee), or 0 if none, for active=1 rows with day between {lo} and {hi}, inclusive, and amount >= {minimum}."
        prompt="SQLite table orders(id INTEGER, region TEXT, amount INTEGER, quantity INTEGER, fee INTEGER, day INTEGER, active INTEGER). "+prompt+" Output only SELECT SQL."
        databases=[]
        for _ in range(3):
            rows=[[i,rng.choice(["east","north","west"]),rng.randint(0,120),rng.randint(1,6),rng.randint(0,8),rng.randint(1,30),rng.randint(0,1)] for i in range(rng.randint(12,25))]
            databases.append({"rows":rows,"output":sql_result(query,rows)})
        return params,prompt,{"databases":databases,"canonical_output":query}
    if family=="tool":
        item=f"item-{rng.randint(100,99999)}";wh=rng.choice(["east","north","west"])
        boxes,per,extra=rng.randint(2,12),rng.randint(2,20),rng.randint(0,8)
        qty=boxes*per+(extra if hard else 0)
        params={"item":item,"warehouse":wh,"boxes":boxes,"per":per,"extra":extra if hard else 0}
        answer={"tool":"reserve_stock","arguments":{"item":item,"warehouse":wh,"quantity":qty,"allow_partial":False}}
        prompt=f"Reserve {boxes} boxes containing {per} units each"+(f", plus {extra} loose units" if hard else "")+f" of {item} from {wh}. Partial fulfilment is prohibited. Return exactly JSON with tool='reserve_stock' and arguments containing item, warehouse, quantity (integer), allow_partial (boolean)."
        return params,prompt,{"answer":answer,"canonical_output":canonical(answer)}
    if family=="visual":
        if not hard:
            n=rng.choice([5,6,7,8,9,10]);target=[rng.randrange(n),rng.randrange(n)]
            params={"kind":"grid","n":n,"target":target}
            answer={"row":target[0]+1,"column":target[1]+1}
            prompt="Inspect the image. Return the red cell's 1-based row (top to bottom) and column (left to right) as JSON with row and column."
        else:
            values=[rng.randint(2,8)*5 for _ in range(4)]
            params={"kind":"chart","values":values}
            answer={"value":values[0]+values[2]-values[1]}
            prompt="Inspect the chart with bars numbered 1 to 4. Return bar 1 + bar 3 - bar 2 as JSON with integer key value. Use the numeric vertical axis."
        return params,prompt,{"answer":answer,"canonical_output":canonical(answer)}
    score,threshold=rng.randint(0,100),rng.randint(20,80)
    risk,limit=rng.randint(0,20),rng.randint(4,16);docs=rng.randint(0,1);member=rng.randint(0,1);hours=rng.randint(1,72);window=rng.randint(6,48)
    label=int(score>=threshold and risk<limit and (not hard or docs and (member or hours<=window)))
    params={"score":score,"threshold":threshold,"risk":risk,"limit":limit,"documents":docs if hard else None,"member":member if hard else None,"hours":hours if hard else None,"window":window if hard else None}
    prompt=f"Eligibility requires score >= {threshold} and risk < {limit}. Applicant score={score}, risk={risk}."
    if hard:prompt+=f" Also require documents present and either membership or hours <= {window}. documents={bool(docs)}, membership={bool(member)}, hours={hours}."
    prompt+=" Is the applicant eligible? Return the probability of yes as JSON with p."
    return params,prompt,{"answer":label,"canonical_output":canonical({"p":label})}

def group_split(group):
    bucket=int(group[:8],16)%100
    return "practice" if bucket<60 else "development" if bucket<75 else "evaluation"

def build(root):
    root=Path(root);config=read_json(root/"task.json")
    seedpath=root/"public-authoring/evaluation_seed.json"
    if seedpath.exists():
        seed=read_json(seedpath)["seed_hex"]
    else:
        seed=secrets.token_hex(16);write_json(seedpath,{"seed_hex":seed,"purpose":"public evaluation seed; included in Work and public release"})
    if len(seed)!=32 or any(c not in "0123456789abcdef" for c in seed):
        raise ContractError("evaluation seed must be 128-bit lowercase hex")
    counts=config["counts"];slug=config["slug"];seen={};all_inputs={};manifest_files={}
    for split in ("practice","development","evaluation"):
        records=[];golds=[]
        for family in FAMILIES:
            count=counts[split]//6
            for ordinal in range(count):
                difficulty="short" if ordinal%2==0 else "compositional"
                root_seed=seed if split=="evaluation" else slug+"-"+("dev" if split=="development" else "practice")+"-v1"
                for attempt in range(100000):
                    material=[root_seed,family,ordinal,attempt]
                    rng=random.Random(int(digest(material),16))
                    params,prompt,gold=make(family,difficulty,rng,ordinal%4//2)
                    # Group all same concrete semantic worlds BEFORE allowing a split or rendering variants.
                    semantic={"family":family,"difficulty":difficulty,"parameters":params}
                    if family=="visual" and params["kind"]=="grid":
                        semantic["parameters"]={k:v for k,v in params.items() if k!="world"}
                    group=digest(semantic)
                    if group_split(group)!=split or group in seen:
                        continue
                    if family=="confidence" and gold["answer"]!=ordinal%4//2:
                        continue
                    break
                else:
                    raise ContractError("group space exhausted for "+family)
                opaque=digest([root_seed,group,"record-id"])[:20]
                record_id=f"{slug}:{split}:{family}:{opaque}"
                seen[group]=split
                row={"id":record_id,"family":family,"difficulty":difficulty,"scenario_group":group,"prompt":prompt,"mode":"system1" if family=="confidence" else "system2","max_output_tokens":160}
                if family=="visual":
                    prefix="data/public"
                    image=f"{prefix}/images/{split}-{ordinal:04d}.png"
                    render(params,root/image);row["image"]=image
                    manifest_files[image]=file_hash(root/image)
                records.append(row);golds.append({"id":record_id,"family":family,"scenario_group":group,**gold})
        random.Random(int(digest([root_seed,"record-order"]),16)).shuffle(records)
        gold_by_id={g["id"]:g for g in golds};golds=[gold_by_id[r["id"]] for r in records]
        ip,gp=paths(root,split);write_jsonl(ip,records);write_jsonl(gp,golds)
        all_inputs[split]=records
        manifest_files[str(ip.relative_to(root))]=file_hash(ip);manifest_files[str(gp.relative_to(root))]=file_hash(gp)
    manifest={"schema":"dataset-manifest-v1","slug":slug,"counts":counts,"families":list(FAMILIES),"difficulty":["short","compositional"],"evaluation_seed_sha256":hashlib.sha256(bytes.fromhex(seed)).hexdigest(),"group_assignment":"SHA256(concrete canonical scenario) first 32 bits modulo 100; 0..59 practice,60..74 development,75..99 evaluation; reject duplicates before render","files":manifest_files}
    write_json(root/"data/manifest.json",manifest)
    probe_ids=[]
    for family in FAMILIES[:-1]:
        chosen=sorted([r["id"] for r in all_inputs["evaluation"] if r["family"]==family],key=lambda s:digest(s))[:16]
        probe_ids.extend(chosen)
    write_json(root/"public-authoring/probe_plan.json",{"ids":probe_ids,"count":80,"vocabulary_size":262144,"position_rule":"floor(L/2) after tokenizing the canonical gold output with pinned tokenizer; tokenizer not downloaded","positions_materialized":False})
    if config["mode"]=="prune":
        profile_ids=[]
        for family in FAMILIES:
            for difficulty in ("short","compositional"):
                profile_ids.extend(sorted(r["id"] for r in all_inputs["practice"] if r["family"]==family and r["difficulty"]==difficulty)[:32])
        if len(profile_ids)!=384:
            raise ContractError("B96 profiling plan coverage mismatch")
        write_json(root/"public-authoring/b96_profile_plan.json",{"schema":"b96-profile-plan-v1","split":"practice","ids":profile_ids,"count":384,"selection":"first 32 lexicographically sorted IDs per family and difficulty","status":"configuration-only-routing-counts-not-measured"})
    template={"schema":"reference-cache-v1","status":"unmaterialized","source_revision":config["source_revision"],"dataset_manifest_sha256":file_hash(root/"data/manifest.json"),"B0":None,"BQ":None,"B96":None,"reason":"No model/GPU measurements exist. Completed operator measurements will be published; never replace nulls with estimates."}
    ref=root/"public-authoring/reference_cache.json"
    if not ref.exists() or read_json(ref).get("status")=="unmaterialized":
        write_json(ref,template)
    audit(root)
    return manifest

def audit(root):
    root=Path(root);cfg=read_json(root/"task.json");manifest=read_json(root/"data/manifest.json");groups={};ids=set();report={}
    for split in ("practice","development","evaluation"):
        ip,gp=paths(root,split);inputs=read_jsonl(ip);gold=read_jsonl(gp)
        if len(inputs)!=cfg["counts"][split] or len(gold)!=len(inputs):
            raise ContractError("wrong split count")
        if {x["id"] for x in inputs}!={x["id"] for x in gold}:
            raise ContractError("gold coverage mismatch")
        c=Counter(x["family"] for x in inputs)
        if set(c)!=set(FAMILIES) or len(set(c.values()))!=1:
            raise ContractError("family imbalance")
        for row in inputs:
            if row["id"] in ids or row["scenario_group"] in groups or group_split(row["scenario_group"])!=split:
                raise ContractError("duplicate or cross-split scenario")
            ids.add(row["id"]);groups[row["scenario_group"]]=split
            if row.get("image"):
                image=root/row["image"]
                if image.read_bytes()[:8]!=b"\x89PNG\r\n\x1a\n":
                    raise ContractError("invalid PNG")
        report[split]=dict(c)
    for name,sha in manifest["files"].items():
        if file_hash(root/name)!=sha:
            raise ContractError("dataset hash mismatch: "+name)
    return {"status":"pass","counts":report,"unique_scenario_groups":len(groups)}
