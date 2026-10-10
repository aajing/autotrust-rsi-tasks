"""Objective CPU oracles. Python is a deliberately restricted expression language."""
import ast
import json
import math
import re
import sqlite3
from fractions import Fraction
from .common import ContractError, canonical

FUNCTIONS={"sum":sum,"len":len,"sorted":sorted,"min":min,"max":max,"abs":abs}
ALLOWED=(ast.Module,ast.FunctionDef,ast.arguments,ast.arg,ast.Return,ast.Name,ast.Load,ast.Store,
ast.Constant,ast.BinOp,ast.UnaryOp,ast.BoolOp,ast.Compare,ast.IfExp,ast.List,ast.Tuple,
ast.ListComp,ast.GeneratorExp,ast.comprehension,ast.Call,ast.keyword,ast.Subscript,ast.Slice,
ast.Add,ast.Sub,ast.Mult,ast.FloorDiv,ast.Mod,ast.USub,ast.UAdd,ast.Not,ast.And,ast.Or,
ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE)

def strip_fence(text):
    if not isinstance(text,str):
        return text
    text=text.strip()
    if text.startswith("```"):
        lines=text.splitlines()
        if len(lines)<3 or lines[-1].strip()!="```":
            raise ContractError("unfinished code fence")
        return "\n".join(lines[1:-1])
    return text

def check_python(source, tests):
    if not isinstance(source,str) or len(source)>4000:
        return False
    try:
        tree=ast.parse(strip_fence(source))
        nodes=list(ast.walk(tree))
        if len(nodes)>180 or len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):
            return False
        f=tree.body[0]
        if f.name!="solve" or f.decorator_list or len(f.body)!=1 or not isinstance(f.body[0],ast.Return):
            return False
        a=f.args
        if len(a.args)!=1 or a.args[0].arg!="xs" or a.defaults or a.kwonlyargs or a.vararg or a.kwarg or a.posonlyargs:
            return False
        for n in nodes:
            if not isinstance(n,ALLOWED):
                return False
            if isinstance(n,ast.Name) and n.id not in {"xs","x","y"} | set(FUNCTIONS):
                return False
            if isinstance(n,ast.Constant) and (not isinstance(n.value,(int,bool)) or abs(n.value)>1000000):
                return False
            if isinstance(n,ast.Call) and (not isinstance(n.func,ast.Name) or n.func.id not in FUNCTIONS):
                return False
            if isinstance(n,ast.comprehension) and (n.is_async or not isinstance(n.iter,ast.Name) or n.iter.id!="xs" or not isinstance(n.target,ast.Name) or n.target.id not in ("x","y")):
                return False
            if isinstance(n,(ast.ListComp,ast.GeneratorExp)) and len(n.generators)!=1:
                return False
        if sum(isinstance(n,(ast.ListComp,ast.GeneratorExp)) for n in nodes)>1:
            return False
        return all(_expression(f.body[0].value,{"xs":list(t["input"])})==t["output"] for t in tests)
    except (Exception,MemoryError):
        return False

def _bounded(value):
    if isinstance(value,(list,tuple)):
        if len(value)>512:raise ContractError("expression output too large")
        for x in value:_bounded(x)
    elif isinstance(value,int):
        if value.bit_length()>128:raise ContractError("integer too large")
    elif value is not None:
        raise ContractError("unsupported expression value")
    return value

def _expression(n,env):
    if isinstance(n,ast.Constant):return n.value
    if isinstance(n,ast.Name):return env[n.id]
    if isinstance(n,(ast.List,ast.Tuple)):
        result=[_expression(x,env) for x in n.elts]
        return _bounded(result if isinstance(n,ast.List) else tuple(result))
    if isinstance(n,ast.UnaryOp):
        x=_expression(n.operand,env)
        return _bounded(-x if isinstance(n.op,ast.USub) else +x if isinstance(n.op,ast.UAdd) else not x)
    if isinstance(n,ast.BinOp):
        a,b=_expression(n.left,env),_expression(n.right,env)
        if not isinstance(a,int) or not isinstance(b,int):raise ContractError("integer arithmetic only")
        if isinstance(n.op,ast.Add):v=a+b
        elif isinstance(n.op,ast.Sub):v=a-b
        elif isinstance(n.op,ast.Mult):v=a*b
        elif isinstance(n.op,ast.FloorDiv):v=a//b
        elif isinstance(n.op,ast.Mod):v=a%b
        else:raise ContractError("unsupported operator")
        return _bounded(v)
    if isinstance(n,ast.BoolOp):
        if isinstance(n.op,ast.And):return all(_expression(x,env) for x in n.values)
        return any(_expression(x,env) for x in n.values)
    if isinstance(n,ast.Compare):
        a=_expression(n.left,env)
        for op,item in zip(n.ops,n.comparators):
            b=_expression(item,env)
            good=(a==b if isinstance(op,ast.Eq) else a!=b if isinstance(op,ast.NotEq) else a<b if isinstance(op,ast.Lt) else a<=b if isinstance(op,ast.LtE) else a>b if isinstance(op,ast.Gt) else a>=b)
            if not good:return False
            a=b
        return True
    if isinstance(n,ast.IfExp):return _expression(n.body if _expression(n.test,env) else n.orelse,env)
    if isinstance(n,(ast.ListComp,ast.GeneratorExp)):
        comp=n.generators[0];result=[]
        for x in env["xs"]:
            local={**env,comp.target.id:x}
            if all(_expression(c,local) for c in comp.ifs):result.append(_expression(n.elt,local))
        return _bounded(result)
    if isinstance(n,ast.Call):
        args=[_expression(x,env) for x in n.args]
        kwargs={x.arg:_expression(x.value,env) for x in n.keywords}
        return _bounded(FUNCTIONS[n.func.id](*args,**kwargs))
    if isinstance(n,ast.Subscript):
        v=_expression(n.value,env)
        if isinstance(n.slice,ast.Slice):
            parts=[_expression(x,env) if x is not None else None for x in (n.slice.lower,n.slice.upper,n.slice.step)]
            return _bounded(v[slice(*parts)])
        return _bounded(v[_expression(n.slice,env)])
    raise ContractError("unsupported expression")

def sql_result(query, rows):
    if not isinstance(query,str) or len(query)>4000 or not query.lstrip().lower().startswith("select"):
        raise ContractError("only SELECT is allowed")
    db=sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE orders (id INTEGER, region TEXT, amount INTEGER, quantity INTEGER, fee INTEGER, day INTEGER, active INTEGER)")
        db.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?)",rows)
        allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION}
        funcs={"sum","count","min","max","avg","coalesce","abs"}
        def authorize(action,arg1,arg2,_db,_trigger):
            if action not in allowed:
                return sqlite3.SQLITE_DENY
            if action==sqlite3.SQLITE_FUNCTION and str(arg2).lower() not in funcs:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        db.set_authorizer(authorize)
        steps=[0]
        def tick():
            steps[0]+=1
            return int(steps[0]>1000)
        db.set_progress_handler(tick,100)
        rows=db.execute(query).fetchmany(1001)
        if len(rows)>1000:
            raise ContractError("SQL output too large")
        return [list(r) for r in rows]
    finally:
        db.close()

def check_sql(query, databases):
    try:
        query=strip_fence(query)
        return all(sql_result(query,d["rows"])==d["output"] for d in databases)
    except Exception:
        return False

def parse_json(value):
    if isinstance(value,str):
        return json.loads(strip_fence(value))
    return value

def confidence(value):
    value=parse_json(value)
    if not isinstance(value,dict) or set(value)!={"p"}:
        raise ContractError("confidence output must be {p:number}")
    p=value["p"]
    if isinstance(p,bool) or not isinstance(p,(int,float)) or not math.isfinite(p) or not 0<=p<=1:
        raise ContractError("invalid probability")
    return float(p)

def evaluate_answer(gold, output):
    family=gold["family"]
    try:
        if family=="python":
            return {"correct":check_python(output,gold["tests"])}
        if family=="sql":
            return {"correct":check_sql(output,gold["databases"])}
        if family=="confidence":
            p=confidence(output);y=gold["answer"]
            return {"correct":int(p>=0.5)==y,"brier":(p-y)**2}
        if family=="math":
            text=str(output).strip()
            if not re.fullmatch(r"-?[0-9]+(?:/[1-9][0-9]*)?",text):
                return {"correct":False}
            return {"correct":Fraction(text)==Fraction(gold["answer"])}
        value=parse_json(output)
        # Canonical JSON equality distinguishes booleans from numbers.
        return {"correct":canonical(value)==canonical(gold["answer"])}
    except Exception:
        return {"correct":False,**({"brier":1.0} if family=="confidence" else {})}
