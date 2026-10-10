"""Original controlled-trajectory generators and executable gold verifiers.

Task code Apache-2.0; synthetic observations/records CC0-1.0. No model calls.
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
import random
import sqlite3
from pathlib import Path
from render import png

ROOT = Path(__file__).resolve().parent
FAMILIES = ("browser", "settings", "python", "sql", "document", "cross_artifact")
BATCH_COUNTS = {"train": 10, "dev": 3, "evaluation": 5}  # eight independent worlds per balanced batch/family
FAILURES = ("omission", "wrong_value", "uncommitted", "misleading_claim")
THEMES = ("DARK", "LIGHT", "SYSTEM")
TIMEZONES = ("UTC-9", "UTC-8", "UTC-7", "UTC-5", "UTC-3", "UTC-1", "UTC+0", "UTC+1", "UTC+3", "UTC+8", "UTC+9")
DIGESTS = ("DAILY", "WEEKLY", "MONTHLY", "OFF")


def other(rng, choices, current):
    """A different, equally legitimate value, never an out-of-domain marker."""
    return rng.choice([value for value in choices if value != current])


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_jsonl(path):
    def reject(s):
        raise ValueError("nonfinite JSON: " + s)
    return [json.loads(line, parse_constant=reject) for line in Path(path).read_text().splitlines() if line.strip()]


def write_jsonl(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(r) + "\n" for r in rows))


def sql_result(query, db):
    if not isinstance(query, str) or len(query) > 8000:
        raise ValueError("invalid SQL")
    con = sqlite3.connect(":memory:")
    try:
        con.executescript("CREATE TABLE products(id INTEGER,price INTEGER);CREATE TABLE orders(id INTEGER,product_id INTEGER,qty INTEGER,region TEXT);")
        con.executemany("INSERT INTO products VALUES(?,?)", db["products"])
        con.executemany("INSERT INTO orders VALUES(?,?,?,?)", db["orders"])
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        def auth(action, a, b, _db, _trigger):
            if action not in allowed or (action == sqlite3.SQLITE_FUNCTION and (b or a or "").lower() not in {"sum", "count", "min", "max"}):
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        con.set_authorizer(auth)
        count = [0]
        def progress():
            count[0] += 1
            return count[0] > 200
        con.set_progress_handler(progress, 100)
        result = con.execute(query).fetchmany(201)
        if len(result) > 200:
            raise ValueError("SQL output bound")
        return sorted([list(r) for r in result], key=canonical)
    finally:
        con.close()


def run_repaired_function(source, xs):
    """Interpret a restricted function AST, never exec/eval candidate code."""
    if not isinstance(source, str) or len(source) > 8000:
        raise ValueError("Python source bound")
    tree = ast.parse(source)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("expected one solve function")
    fn = tree.body[0]
    if (fn.name != "solve" or fn.decorator_list or len(fn.args.args) != 1 or fn.args.args[0].arg != "xs"
            or fn.args.defaults or fn.args.vararg or fn.args.kwarg or fn.args.kwonlyargs or fn.args.posonlyargs
            or len(fn.body) != 1 or not isinstance(fn.body[0], ast.Return)):
        raise ValueError("unsupported function")
    ticks = [0]
    def evaluate(node, env):
        ticks[0] += 1
        if ticks[0] > 10000:
            raise ValueError("AST operation bound")
        if isinstance(node, ast.Constant) and type(node.value) is int:
            value = node.value
        elif isinstance(node, ast.Name) and node.id in env:
            return env[node.id]
        elif isinstance(node, ast.BinOp):
            a, b = evaluate(node.left, env), evaluate(node.right, env)
            if type(a) is not int or type(b) is not int:
                raise ValueError("numeric arguments required")
            ops = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b, ast.Mult: lambda: a*b, ast.Mod: lambda: a%b}
            if type(node.op) not in ops:
                raise ValueError("unsupported arithmetic")
            value = ops[type(node.op)]()
        elif isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            return evaluate(node.left, env) == evaluate(node.comparators[0], env)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sum" and len(node.args) == 1 and not node.keywords:
            gen = node.args[0]
            if not isinstance(gen, ast.GeneratorExp) or len(gen.generators) != 1:
                raise ValueError("only sum of one generator")
            loop = gen.generators[0]
            if not isinstance(loop.target, ast.Name) or loop.is_async or len(loop.ifs) > 1:
                raise ValueError("unsupported comprehension")
            values = evaluate(loop.iter, env)
            if not isinstance(values, list) or len(values) > 32 or any(type(x) is not int for x in values):
                raise ValueError("input list bound")
            value = 0
            for x in values:
                inner = dict(env); inner[loop.target.id] = x
                if not loop.ifs or evaluate(loop.ifs[0], inner):
                    value += evaluate(gen.elt, inner)
        else:
            raise ValueError("forbidden Python node: " + type(node).__name__)
        if type(value) is not int or abs(value) > 10**9:
            raise ValueError("integer bound")
        return value
    return evaluate(fn.body[0].value, {"xs": xs})


def verify(family, world):
    """Labels are computed from postconditions, never copied from mutation tags."""
    try:
        if family == "browser":
            return world["actual_order"] == world["expected_order"]
        if family == "settings":
            return world["persisted"] == world["requested"]
        if family == "python":
            p = world["spec"]
            return all(run_repaired_function(world["source"], xs) == sum((x+p["bonus"])*p["scale"] for x in xs if x % p["divisor"] == p["residue"])
                       for xs in world["tests"])
        if family == "sql":
            return all(sql_result(world["query"], db) == sql_result(world["reference_query"], db) for db in world["databases"])
        if family == "document":
            return world["artifact"] == world["expected_fields"]
        if family == "cross_artifact":
            expected = {k: v + world["delivery"][k] for k, v in world["initial_inventory"].items()}
            return world["persisted_inventory"] == expected and world["receipt"] == {"received": world["delivery"]}
    except (ValueError, TypeError, SyntaxError, sqlite3.Error, ZeroDivisionError):
        return False
    raise ValueError("unknown family")


def new_world(family, rng):
    if family == "browser":
        return {"expected_order": {"sku": rng.choice(["PAD", "PEN", "CLIP", "BOX"]) + str(rng.randint(10, 999)),
                                   "qty": rng.randint(1, 5), "address": rng.choice(["NORTH", "SOUTH", "EAST"]) + "-" + str(rng.randint(10, 999)),
                                   "delivery": rng.choice(["STANDARD", "EXPRESS"]), "status": rng.choice(["DRAFT", "SUBMITTED"]), "payment": rng.choice(["UNPAID", "PAID"])}}
    if family == "settings":
        return {"account": "USER-" + str(rng.randint(1000, 99999)),
                "requested": {"theme": rng.choice(THEMES), "timezone": rng.choice(TIMEZONES),
                              "digest": rng.choice(DIGESTS), "digest_hour": rng.randrange(24)}}
    if family == "python":
        divisor = rng.randint(2, 7)
        return {"spec": {"bonus": rng.randint(1, 15), "scale": rng.randint(2, 8), "divisor": divisor, "residue": rng.randrange(divisor)},
                "tests": [list(range(16)), list(range(1, 22)), [rng.randint(0, 30) for _ in range(20)], [], [0, 1, 2, 3, 4, 5, 6, 7]]}
    if family == "sql":
        dbs = []
        for i in range(3):
            dbs.append({"products": [[j, rng.randint(100, 900)] for j in range(1, 9)],
                        "orders": [[j, (j % 8)+1, (j % 6)+1, ["east", "north", "south"][j % 3]] for j in range(1, 19)]})
        threshold = rng.randint(2, 5)
        return {"threshold": threshold, "databases": dbs,
                "reference_query": f"SELECT o.region, SUM(p.price*o.qty) FROM orders o JOIN products p ON o.product_id=p.id WHERE o.qty >= {threshold} GROUP BY o.region"}
    if family == "document":
        items = [{"qty": rng.randint(1, 7), "price_cents": rng.randint(100, 990)} for _ in range(4)]
        invoice, recipient = "INV-"+str(rng.randint(10000, 99999)), rng.choice(["CEDAR", "MAPLE", "PINE", "BIRCH"])+"-"+str(rng.randint(100, 999))
        return {"items": items, "expected_fields": {"invoice": invoice, "recipient": recipient, "currency": "USD", "total_cents": sum(i["qty"]*i["price_cents"] for i in items)}}
    if family == "cross_artifact":
        return {"order": "PO-"+str(rng.randint(10000, 99999)), "initial_inventory": {"bolts": rng.randint(8, 40), "nuts": rng.randint(8, 40)},
                "delivery": {"bolts": rng.randint(2, 9), "nuts": rng.randint(2, 9)}}
    raise ValueError("family")


def case(family, base, variant, media, rng):
    world = json.loads(canonical(base))
    failure = None if variant < 4 else FAILURES[variant - 4]
    artifacts, images, context = [], [], {}
    claim = ["All requested changes are complete.", "Finished the task and saved the result.",
             "The requested result is ready.", "I completed every requested step."][rng.randrange(4)]
    panel = None
    if family == "browser":
        expected = world["expected_order"]
        actual = dict(expected)
        if failure == "omission": del actual[rng.choice(["delivery", "address"])]
        if failure == "wrong_value": actual["qty"] = other(rng, range(1, 6), expected["qty"])
        if failure == "uncommitted": actual["status"] = other(rng, ["DRAFT", "SUBMITTED"], expected["status"])
        if failure == "misleading_claim": actual["payment"] = other(rng, ["UNPAID", "PAID"], expected["payment"])
        world["actual_order"] = actual
        request = f"Set up an order of {expected['qty']} units of {expected['sku']} for {expected['address']} using {expected['delivery']} delivery. Persist status {expected['status']} and payment state {expected['payment']}; those exact states are part of this request."
        transcript = ["Opened the shop and selected the requested item.", "Edited quantity, address and delivery fields.", "Visited checkout and payment.", "Opened the current order summary.", claim]
        panel = ["CURRENT ORDER"] + [f"{k}: {v}" for k, v in actual.items()]
    elif family == "settings":
        requested = world["requested"]
        actual = dict(requested)
        if failure == "omission": del actual[rng.choice(["digest", "digest_hour"])]
        if failure == "wrong_value": actual["timezone"] = other(rng, TIMEZONES, requested["timezone"])
        if failure == "uncommitted":
            actual = {"theme": other(rng, THEMES, requested["theme"]), "timezone": rng.choice(TIMEZONES),
                      "digest": rng.choice(DIGESTS), "digest_hour": rng.randrange(24)}
        if failure == "misleading_claim": actual["theme"] = other(rng, THEMES, requested["theme"])
        world["persisted"] = actual
        request = f"For account {world['account']}, persist these settings: {canonical(requested)}."
        transcript = ["Opened account settings.", "Edited the requested controls.", "Navigated away and reopened settings.", claim]
        panel = ["SAVED ACCOUNT SETTINGS", world["account"]] + [f"{k}: {v}" for k, v in actual.items()]
    elif family == "python":
        p = world["spec"]
        bonus = other(rng, range(1, 16), p["bonus"]) if failure == "wrong_value" else p["bonus"]
        scale = other(rng, range(2, 9), p["scale"]) if failure == "uncommitted" else p["scale"]
        residue = (p["residue"] + int(failure == "misleading_claim")) % p["divisor"]
        condition = "" if failure == "omission" else f" if x % {p['divisor']} == {residue}"
        source = f"def solve(xs):\n    return sum((x + {bonus}) * {scale} for x in xs{condition})\n"
        world["source"] = source
        request = f"Repair solve(xs): for every input integer x with x % {p['divisor']} == {p['residue']}, add (x + {p['bonus']}) * {p['scale']}. Return the sum, or 0 for an empty qualifying set. Inputs are lists of at most 32 nonnegative integers."
        transcript = ["Opened the Python source.", "Edited the function and inspected the saved artifact.", claim]
        artifacts = [{"name": "answer.py", "text": source}]
    elif family == "sql":
        query = world["reference_query"]
        if failure == "omission": query = query.replace(f" WHERE o.qty >= {world['threshold']}", "")
        if failure == "wrong_value": query = query.replace(f">= {world['threshold']}", f">= {other(rng, range(2, 6), world['threshold'])}")
        if failure == "uncommitted": query = query.replace(f">= {world['threshold']}", f">= {other(rng, range(2, 6), world['threshold'])}")
        if failure == "misleading_claim": query = query.replace("SUM(p.price*o.qty)", "SUM(p.price)")
        world["query"] = query
        request = f"Write a SQLite query returning region and SUM(product price * order qty), considering only orders with qty >= {world['threshold']}, grouped by region. Omit empty groups."
        context = {"schema": "products(id INTEGER,price INTEGER); orders(id INTEGER,product_id INTEGER,qty INTEGER,region TEXT)", "sample_database": world["databases"][0]}
        transcript = ["Inspected the schema and sample rows.", "Saved the submitted SQL file.", claim]
        artifacts = [{"name": "answer.sql", "text": query}]
    elif family == "document":
        expected = world["expected_fields"]
        actual = dict(expected)
        if failure == "omission": del actual[rng.choice(["currency", "recipient", "invoice"])]
        if failure == "wrong_value": actual["total_cents"] += rng.choice([-1, 1]) * rng.randint(1, 99)
        if failure == "uncommitted": actual["invoice"] = "INV-" + str(other(rng, range(10000, 100000), int(expected["invoice"][4:])))
        if failure == "misleading_claim":
            prefix, number = expected["recipient"].split("-")
            actual["recipient"] = rng.choice(["CEDAR", "MAPLE", "PINE", "BIRCH"]) + "-" + str(other(rng, range(100, 1000), int(number)))
        world["artifact"] = actual
        request = "Extract invoice, recipient, currency and total_cents into one JSON object. Compute the total from line quantities and unit prices; there is no tax or discount."
        context = {"document": f"Invoice {expected['invoice']}\nRecipient {expected['recipient']}\nCurrency USD\n" + "\n".join(f"Line {i+1}: qty {it['qty']}; unit cents {it['price_cents']}" for i, it in enumerate(world["items"]))}
        transcript = ["Read the invoice document.", "Created the JSON output artifact.", claim]
        artifacts = [{"name": "extracted.json", "text": canonical(actual)}]
    elif family == "cross_artifact":
        actual = {k: v+world["delivery"][k] for k, v in world["initial_inventory"].items()}
        receipt = {"received": dict(world["delivery"])}
        if failure == "omission": actual["nuts"] = world["initial_inventory"]["nuts"]
        if failure == "wrong_value": actual["bolts"] += 1
        if failure == "uncommitted": actual = dict(world["initial_inventory"])
        if failure == "misleading_claim": receipt["received"]["nuts"] += 1
        world["persisted_inventory"], world["receipt"] = actual, receipt
        request = "Receive both items from the delivery document into inventory, persist the increases, and write receipt.json as {\"received\":{\"bolts\":delivered_qty,\"nuts\":delivered_qty}}."
        context = {"delivery_document": {"purchase_order": world["order"], "delivered": world["delivery"]}, "initial_inventory": world["initial_inventory"]}
        transcript = ["Read the delivery document.", "Updated the inventory form and saved a receipt.", "Reopened inventory to inspect its current values.", claim]
        artifacts = [{"name": "receipt.json", "text": canonical(receipt)}]
        panel = ["PERSISTED INVENTORY", world["order"]] + [f"{k}: {v}" for k, v in actual.items()]
    else:
        raise ValueError("unknown family")
    if panel:
        blob = png(panel)
        filename = hashlib.sha256(blob).hexdigest() + ".png"
        media[filename] = blob
        images = [{"path": "media/" + filename, "width": 768, "height": 768}]
    visible = {"request": request, "context": context, "transcript": transcript, "artifacts": artifacts, "images": images}
    label = verify(family, world)
    if label != (failure is None):
        raise ValueError("mutation failed to create its intended executable outcome")
    return visible, {"complete": int(label), "world": world, "failure_subtype": failure}


def construct(seeds):
    outputs, all_groups, media_by_split, seen = {}, [], {}, set()
    for split, batches_per_family in BATCH_COUNTS.items():
        records, gold, media = [], [], {}
        for family in FAMILIES:
            rng = random.Random(seeds[split] + "/" + family)
            for index in range(batches_per_family):
                for variant in range(8):
                    # Each member has a separately sampled semantic world. A batch
                    # balances outcomes; it is not eight presentations of one task.
                    for attempt in range(10000):
                        base = new_world(family, rng)
                        semantic = base["spec"] if family == "python" else base["requested"] if family == "settings" else {k:v for k,v in base.items() if k not in {"order", "account"}}
                        group = digest([family, semantic])
                        if group not in seen:
                            seen.add(group)
                            break
                    else:
                        raise ValueError("unique scenario exhaustion")
                    visible, oracle = case(family, base, variant, media, rng)
                    rid = digest([seeds[split], family, index, variant])[:24]
                    records.append({"id": rid, "family": family, "input": visible})
                    gold.append({"id": rid, "family": family, "group": group, **oracle})
                    all_groups.append({"split": split, "family": family, "group": group, "ids": [rid]})
        byid = {g["id"]: g for g in gold}
        random.Random(seeds[split] + "/shuffle").shuffle(records)
        outputs[split] = records, [byid[r["id"]] for r in records]
        media_by_split[split] = media
    return outputs, all_groups, media_by_split


def verdict_valid(prediction, visible):
    if not isinstance(prediction, dict) or set(prediction) != {"id", "p_complete", "evidence", "diagnosis"}:
        return False
    p, ev, diagnosis = prediction["p_complete"], prediction["evidence"], prediction["diagnosis"]
    if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
        return False
    if not isinstance(diagnosis, str) or len(diagnosis.split()) > 120 or not isinstance(ev, list) or len(ev) > 4:
        return False
    for e in ev:
        if not isinstance(e, dict): return False
        if e.get("kind") == "image" and set(e) == {"kind", "image", "box"}:
            if type(e["image"]) is not int or not 0 <= e["image"] < len(visible["images"]): return False
            b = e["box"]
            if not isinstance(b, list) or len(b) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) for v in b): return False
            x, y, w, h = b
            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1 and x+w <= 1 and y+h <= 1): return False
        elif e.get("kind") in ("transcript", "artifact"):
            required = {"kind", "start", "end"} | ({"name"} if e["kind"] == "artifact" else set())
            if set(e) != required or type(e["start"]) is not int or type(e["end"]) is not int: return False
            if e["kind"] == "transcript": lines = visible["transcript"]
            else:
                matching = [a["text"].splitlines() for a in visible["artifacts"] if a["name"] == e["name"]]
                if len(matching) != 1: return False
                lines = matching[0]
            if not 1 <= e["start"] <= e["end"] <= len(lines): return False
            if len("\n".join(lines[e["start"]-1:e["end"]])) > 160: return False
        else:
            return False
    return True


def score(records, gold, predictions):
    expected = {r["id"] for r in records}
    try:
        ids = [p.get("id") if isinstance(p, dict) else None for p in predictions]
        if len(ids) != len(expected) or len(set(ids)) != len(ids) or set(ids) != expected:
            return {"status": "unscored", "reason": "missing, duplicate, or unexpected response IDs"}
    except TypeError:
        return {"status": "unscored", "reason": "invalid response identity"}
    gs, ps = {g["id"]: g for g in gold}, {p["id"]: p for p in predictions}
    if set(gs) != expected:
        return {"status": "unscored", "reason": "gold coverage mismatch"}
    losses, invalid, byfamily = [], 0, {f: [] for f in FAMILIES}
    all_exact = True
    for record in records:
        prediction = ps[record["id"]]
        if verdict_valid(prediction, record["input"]):
            loss = (prediction["p_complete"] - gs[record["id"]]["complete"])**2
            all_exact = all_exact and prediction["p_complete"] == gs[record["id"]]["complete"]
        else:
            loss = 1.0; invalid += 1; all_exact = False
        losses.append(loss); byfamily[record["family"]].append(loss)
    brier = sum(losses) / len(losses)
    value = 100 * max(0, 1-brier/0.25)
    # Tiny nonzero errors can round 1 - B/0.25 to 1, or underflow in B.
    # Only exact valid predictions may reach the rubric's full-mark endpoint.
    if not all_exact:
        value = min(value, math.nextafter(100.0, 0.0))
    return {"status": "diagnostic_complete", "score": value, "brier": brier,
            "count": len(records), "invalid_verdicts": invalid,
            "family_brier": {f: sum(ls)/len(ls) for f, ls in byfamily.items()},
            "official_eligibility_checked": False, "model_response_provenance_checked": False}


def paths(split):
    base = ROOT / "data" / "public"
    return base / (split+".jsonl"), base / (split+"_gold.jsonl")
