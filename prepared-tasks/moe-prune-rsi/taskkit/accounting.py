"""Budget ledger validation; timestamps/source tokens still need a trusted GPU adapter."""
from .common import ContractError

def validate_ledger(events,mode):
    seen=set();inference=training=updates=0;work_seconds=0.0
    for event in events:
        if set(event)!={"event_id","kind","input_tokens","output_tokens","seconds","optimizer_updates"}:
            raise ContractError("invalid ledger schema")
        if event["event_id"] in seen:raise ContractError("duplicate receipt ID")
        seen.add(event["event_id"])
        if event["kind"] not in ("inference","training","cpu"):
            raise ContractError("unknown operation")
        for name in ("input_tokens","output_tokens","optimizer_updates"):
            if type(event[name])!=int or event[name]<0:raise ContractError("invalid token/update receipt")
        if isinstance(event["seconds"],bool) or not isinstance(event["seconds"],(int,float)) or not 0<=event["seconds"]<float("inf"):
            raise ContractError("invalid time")
        work_seconds+=event["seconds"]
        tokens=event["input_tokens"]+event["output_tokens"]
        if event["kind"]=="inference":
            if event["optimizer_updates"]:raise ContractError("inference receipt cannot hide optimizer updates")
            inference+=tokens
        elif event["kind"]=="training":training+=tokens;updates+=event["optimizer_updates"]
        elif tokens or event["optimizer_updates"]:raise ContractError("CPU receipt cannot hide model work")
    if inference>500000 or work_seconds>7200 or training>(250000 if mode=="prune" else 0) or updates>(512 if mode=="prune" else 0):
        raise ContractError("Work budget exceeded")
    return {"inference_tokens":inference,"training_token_exposures":training,"updates":updates,"charged_seconds":work_seconds}
