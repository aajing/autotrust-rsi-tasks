import argparse
import json
from pathlib import Path
from .common import ContractError,write_json,paths,read_jsonl
from .data import build,audit
from .scoring import assess,aggregate

def main():
    p=argparse.ArgumentParser(description="CPU task preparation and assessment; no GPU execution")
    sub=p.add_subparsers(dest="command",required=True)
    b=sub.add_parser("build");b.add_argument("--root",default=".")
    a=sub.add_parser("audit");a.add_argument("--root",default=".")
    u=sub.add_parser("public-assess");u.add_argument("--root",default=".");u.add_argument("--split",choices=("practice","development","evaluation"),default="development");u.add_argument("--predictions",required=True)
    s=sub.add_parser("assess");s.add_argument("--root",default=".");s.add_argument("--predictions",required=True);s.add_argument("--resources",required=True);s.add_argument("--references",required=True);s.add_argument("--probe-dir");s.add_argument("--expert-map");s.add_argument("--output")
    args=p.parse_args()
    try:
        if args.command=="build":result={"status":"built","counts":build(args.root)["counts"]}
        elif args.command=="audit":result=audit(args.root)
        elif args.command=="public-assess":
            ip,gp=paths(args.root,args.split)
            result={"status":"public_assessment","official_reward":False,"metrics":aggregate(read_jsonl(ip),read_jsonl(gp),read_jsonl(args.predictions))}
        else:result=assess(args.root,args.predictions,args.resources,args.references,args.probe_dir,args.expert_map)
    except (ContractError,OSError,KeyError,ValueError,TypeError) as e:
        result={"status":"unscored","official_reward":False,"reason":str(e)}
    if getattr(args,"output",None):write_json(args.output,result)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2 if result.get("status")=="unscored" else 0

if __name__=="__main__":
    raise SystemExit(main())
