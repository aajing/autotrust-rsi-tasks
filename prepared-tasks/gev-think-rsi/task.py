"""CPU task construction and diagnostic evaluation. No model inference.

Original task code, Apache-2.0. Synthetic records: CC0-1.0.
Generated Python is interpreted by a bounded AST interpreter, never eval/exec.
"""
from __future__ import annotations
import ast
import hashlib
import json
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAMILIES = ("python", "sql", "invoice", "schedule", "workflow")
COUNTS = {"train": 100, "dev": 20, "evaluation": 40}  # per family; all splits and gold are public


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_jsonl(path):
    def reject(value):
        raise ValueError("nonfinite JSON: " + value)
    records = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            records.append(json.loads(line, parse_constant=reject))
    return records


def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(r) + "\n" for r in records))


def run_python(source):
    """Small bounded arithmetic language; no imports/calls except range in for."""
    if len(source) > 10000:
        raise ValueError("source too large")
    tree = ast.parse(source)
    env, ticks = {}, [0]

    def tick():
        ticks[0] += 1
        if ticks[0] > 20000:
            raise ValueError("AST budget exceeded")

    def expr(node):
        tick()
        if isinstance(node, ast.Constant) and type(node.value) is int:
            val = node.value
        elif isinstance(node, ast.Name):
            val = env[node.id]
        elif isinstance(node, ast.BinOp):
            a, b = expr(node.left), expr(node.right)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b,
                   ast.Mult: lambda: a * b, ast.Mod: lambda: a % b,
                   ast.FloorDiv: lambda: a // b}
            if type(node.op) not in ops:
                raise ValueError("forbidden arithmetic")
            val = ops[type(node.op)]()
        elif isinstance(node, ast.Compare) and len(node.ops) == 1:
            a, b = expr(node.left), expr(node.comparators[0])
            ops = {ast.Eq: a == b, ast.NotEq: a != b, ast.Lt: a < b,
                   ast.LtE: a <= b, ast.Gt: a > b, ast.GtE: a >= b}
            if type(node.ops[0]) not in ops:
                raise ValueError("forbidden comparison")
            return ops[type(node.ops[0])]
        else:
            raise ValueError("forbidden expression: " + type(node).__name__)
        if type(val) is not int or abs(val) > 10**9:
            raise ValueError("integer bound")
        return val

    def block(nodes):
        for node in nodes:
            tick()
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                env[node.targets[0].id] = expr(node.value)
            elif isinstance(node, ast.If):
                block(node.body if expr(node.test) else node.orelse)
            elif isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                it = node.iter
                if not (isinstance(it, ast.Call) and isinstance(it.func, ast.Name)
                        and it.func.id == "range" and len(it.args) == 1 and not it.keywords and not node.orelse):
                    raise ValueError("only bounded range is allowed")
                n = expr(it.args[0])
                if not 0 <= n <= 64:
                    raise ValueError("range bound")
                for i in range(n):
                    env[node.target.id] = i
                    block(node.body)
            else:
                raise ValueError("forbidden statement: " + type(node).__name__)
    block(tree.body)
    return env


def sql_result(sql, database):
    """Read-only SQLite with one statement, instruction/row/output bounds."""
    if not isinstance(sql, str) or len(sql) > 8000:
        raise ValueError("SQL length/type")
    con = sqlite3.connect(":memory:")
    try:
        con.executescript("CREATE TABLE products(id INTEGER,category TEXT,price INTEGER);"
                          "CREATE TABLE orders(id INTEGER,product_id INTEGER,qty INTEGER,region TEXT);")
        con.executemany("INSERT INTO products VALUES(?,?,?)", database["products"])
        con.executemany("INSERT INTO orders VALUES(?,?,?,?)", database["orders"])
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        permitted_functions = {"sum", "count", "min", "max", "abs", "coalesce"}
        def authorize(action, a, b, _db, _trigger):
            if action not in allowed:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_FUNCTION and (b or a or "").lower() not in permitted_functions:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        con.set_authorizer(authorize)
        calls = [0]
        def progress():
            calls[0] += 1
            return calls[0] > 200  # 20,000 virtual-machine instructions
        con.set_progress_handler(progress, 100)
        rows = con.execute(sql).fetchmany(201)
        if len(rows) > 200 or len(canonical(rows)) > 32768:
            raise ValueError("SQL output bound")
        return sorted([list(row) for row in rows], key=canonical)
    finally:
        con.close()


def database(rng):
    products = [[i, rng.choice(["hardware", "books", "office", "food"]), rng.randint(80, 1900)] for i in range(1, 9)]
    orders = [[i, rng.randint(1, 8), rng.randint(1, 7), rng.choice(["north", "south", "east"])] for i in range(1, rng.randint(12, 24)+1)]
    return {"products": products, "orders": orders}


def schedule_valid(answer, context):
    if not isinstance(answer, dict) or set(answer) != {"schedule"} or not isinstance(answer["schedule"], list):
        return False
    jobs = {j["id"]: j for j in context["jobs"]}
    starts = {}
    for entry in answer["schedule"]:
        if not isinstance(entry, dict) or set(entry) != {"job", "start"}:
            return False
        jid, start = entry["job"], entry["start"]
        if not isinstance(jid, str) or jid in starts or jid not in jobs or type(start) is not int:
            return False
        starts[jid] = start
    if set(starts) != set(jobs):
        return False
    for jid, job in jobs.items():
        start, end = starts[jid], starts[jid] + job["duration"]
        if start < job["release"] or end > job["deadline"]:
            return False
        if any(start < starts[p] + jobs[p]["duration"] for p in job["after"]):
            return False
        for oid, other in jobs.items():
            if oid != jid and other["resource"] == job["resource"]:
                if max(start, starts[oid]) < min(end, starts[oid] + other["duration"]):
                    return False
    return True


def workflow_valid(answer, context):
    if not isinstance(answer, dict) or set(answer) != {"actions"} or not isinstance(answer["actions"], list):
        return False
    if len(answer["actions"]) > 8:
        return False
    state = json.loads(canonical(context["items"]))
    targets = {t["item"]: t for t in context["targets"]}
    for action in answer["actions"]:
        if not isinstance(action, dict) or not {"op", "item"} <= set(action):
            return False
        item = action["item"]
        if not isinstance(item, str) or item not in targets:
            return False
        obj, target = state[item], targets[item]
        op = action["op"]
        if op == "reserve" and set(action) == {"op", "item", "qty"} and obj["status"] == "stock":
            if any(state[p]["status"] != "archived" for p in target.get("after", [])):
                return False
            if type(action["qty"]) is not int or action["qty"] != target["qty"] or not 0 < action["qty"] <= obj["stock"]:
                return False
            obj["reserved"], obj["status"] = action["qty"], "reserved"
        elif op == "move" and set(action) == {"op", "item", "to"} and obj["status"] == "reserved":
            if action["to"] != target["to"]:
                return False
            obj["location"], obj["status"] = action["to"], "moved"
        elif op == "confirm" and set(action) == {"op", "item"} and obj["status"] == "moved":
            obj["status"] = "confirmed"
        elif op == "archive" and set(action) == {"op", "item"} and obj["status"] == "confirmed":
            obj["status"] = "archived"
        else:
            return False
    return all(state[k]["status"] == "archived" and state[k]["reserved"] == t["qty"]
               and state[k]["location"] == t["to"] for k, t in targets.items())


def make_group(family, rng):
    """Two related difficulty variants remain in the same split."""
    if family == "python":
        a, b, mul, bias, modulus, divisor = (rng.randint(1, 19), rng.randint(1, 19), rng.randint(2, 7),
                                           rng.randint(1, 17), rng.randint(41, 199), rng.randint(2, 7))
        loop = rng.randint(3, 7)
        update = rng.choice([f"x * {mul} + i + {bias}", f"(x + i) * {mul} + {bias}", f"x + y // {mul} + i * {bias}"])
        comparison = rng.choice([f"x % {divisor} == 0", f"x % {divisor} != 0", f"x % {divisor} < {divisor//2}"])
        source = (f"x = {a}\ny = {b}\nfor i in range({loop}):\n"
                  f"    x = ({update}) % {modulus}\n"
                  f"    if {comparison}:\n        y = y + x\n    else:\n        y = y - i\n"
                  "result = x + y\n")
        extra = (f"for j in range({rng.randint(3, 6)}):\n    for k in range({rng.randint(2, 4)}):\n"
                 f"        result = (result + j * {rng.randint(3, 15)} + k * y) % {rng.randint(89, 239)}\n"
                 f"    if result % 2 == 0:\n        result = result + x\n    else:\n        result = result - y\n")
        records = []
        for difficulty, program in (("direct", source), ("compositional", source + extra)):
            records.append(({"request": "Return the final integer variable result as JSON {\"value\": integer}. Python integer semantics apply.",
                             "program": program}, {"answer": {"value": run_python(program)["result"]}}))
        return records
    if family == "sql":
        dbs = [database(rng) for _ in range(3)]
        threshold = rng.randint(2, 5)
        grouping, group_name = rng.choice([("p.category", "product category"), ("o.region", "region")])
        aggregate, aggregate_name = rng.choice([("SUM(p.price * o.qty)", "total price*qty"), ("MAX(p.price * o.qty)", "maximum price*qty"), ("SUM(o.qty)", "total quantity")])
        price_bound, having = rng.randint(200, 1200), rng.randint(1, 3)
        queries = [
            f"SELECT {grouping}, COUNT(*) FROM products p JOIN orders o ON p.id=o.product_id WHERE o.qty >= {threshold} GROUP BY {grouping}",
            f"SELECT {grouping}, {aggregate} FROM products p JOIN orders o ON p.id=o.product_id WHERE o.qty >= {threshold} AND p.price >= {price_bound} GROUP BY {grouping} HAVING COUNT(*) >= {having}"]
        requests = [f"Write one read-only SQLite SELECT returning {group_name} and count of order rows with qty >= {threshold}, grouped by {group_name}. Omit empty groups. Do not hard-code observed result values.",
                    f"Write one read-only SQLite SELECT returning {group_name} and {aggregate_name} for order rows with qty >= {threshold} and product price >= {price_bound}, grouped by {group_name}. Keep only groups with at least {having} qualifying order rows. Do not hard-code observed result values."]
        return [({"request": req + ' Respond {"sql": "query"}.', "schema": {"products": ["id INTEGER", "category TEXT", "price INTEGER"], "orders": ["id INTEGER", "product_id INTEGER", "qty INTEGER", "region TEXT"]}, "database": dbs[0]},
                 {"answer": {"sql": query}, "check_databases": dbs,
                  "expected_results": [sql_result(query, db) for db in dbs]}) for req, query in zip(requests, queries)]
    if family == "invoice":
        items = [{"item": name, "qty": rng.randint(1, 7), "unit_cents": rng.randint(100, 4500)} for name in ("paper", "pens", "clips", "folders", "labels", "tape", "pads", "boxes")]
        discount, tax = rng.choice([500, 1000, 1500, 2000]), rng.choice([500, 750, 1000])
        rounding = rng.choice(["invoice", "line"])
        result = []
        for n, complex_ in ((4, False), (8, True)):
            subtotal = sum(it["qty"] * it["unit_cents"] for it in items[:n])
            discounted = (subtotal * (10000 - discount) + 5000) // 10000
            if rounding == "line":
                discounted = sum((it["qty"] * it["unit_cents"] * (10000-discount) + 5000)//10000 for it in items[:n])
            total = discounted + (discounted * tax + 5000) // 10000 if complex_ else subtotal
            req = ("Compute subtotal of the four line items before discount/tax." if not complex_ else
                   ("Compute total: apply discount to the whole subtotal and round to cents half up. " if rounding == "invoice" else
                    "Compute total: discount each line's qty*unit_cents and round that line half up, then sum the discounted lines. ") +
                   "Compute tax on the discounted subtotal and round tax half up, then add. Rates are basis points out of 10000.")
            result.append(({"request": req + ' Return {"total_cents": integer}.', "items": items[:n],
                            "discount_basis_points": discount if complex_ else 0, "tax_basis_points": tax if complex_ else 0}, {"answer": {"total_cents": total}}))
        return result
    if family == "schedule":
        jobs, starts, resource_end = [], {}, {"A": 0, "B": 0}
        for i in range(10):
            jid, resource, duration, release = f"J{i+1}", rng.choice(["A", "B"]), rng.randint(1, 5), rng.randint(0, 5)
            parents = [f"J{j}" for j in rng.sample(range(1, i+1), rng.randint(0, min(i, 2)))]
            start = max([release, resource_end[resource]] + [starts[p] + jobs[int(p[1:])-1]["duration"] for p in parents])
            starts[jid], resource_end[resource] = start, start + duration
            jobs.append({"id": jid, "resource": resource, "duration": duration, "release": release,
                         "deadline": start + duration + rng.randint(1, 5), "after": parents})
        return [({"request": 'Return {"schedule":[{"job":"J1","start":0},...]}, one integer start per job. Respect releases, deadlines, fixed resources without overlap, and after dependencies; intervals are [start,end). Any valid schedule is accepted.',
                  "jobs": rng.sample(jobs[:n], n)}, {"answer": {"schedule": [{"job": j["id"], "start": starts[j["id"]]} for j in jobs[:n]]}}) for n in (6, 10)]
    if family == "workflow":
        items = {name: {"stock": rng.randint(5, 15), "location": rng.choice(["A", "B", "C"]), "status": "stock"} for name in ("bolts", "washers", "nuts", "hinges")}
        names = rng.sample(list(items), 2)
        targets = [{"item": name, "qty": rng.randint(1, 4), "to": rng.choice(["D", "E", "F"])} for name in names]
        if rng.choice([False, True]):
            targets[1]["after"] = [targets[0]["item"]]
        result = []
        for n in (1, 2):
            actions = []
            for t in targets[:n]:
                actions += [{"op": "reserve", "item": t["item"], "qty": t["qty"]},
                            {"op": "move", "item": t["item"], "to": t["to"]},
                            {"op": "confirm", "item": t["item"]}, {"op": "archive", "item": t["item"]}]
            result.append(({"request": 'Return {"actions":[...]}. For each target reserve exact qty, move to destination, confirm, then archive. A target with an after list can be reserved only after every listed item is archived. Use op/item plus qty for reserve or to for move. Other items must stay unchanged. Maximum eight actions.', "items": items, "targets": targets[:n]}, {"answer": {"actions": actions}}))
        return result
    raise ValueError("unknown family")


def construct(seeds):
    """No split identity enters input; identical scenario groups are rejected."""
    outputs, groups, seen = {}, [], set()
    for split, per_family in COUNTS.items():
        inputs, gold = [], []
        for family in FAMILIES:
            rng = random.Random(seeds[split] + "/" + family)
            for index in range(per_family // 2):
                for _attempt in range(10000):
                    variants = make_group(family, rng)
                    group = digest([x[0] for x in variants])
                    if group not in seen:
                        seen.add(group)
                        break
                else:
                    raise ValueError("unique group exhaustion")
                ids = []
                for variant, (context, oracle) in enumerate(variants):
                    rid = digest([seeds[split], family, index, variant])[:24]
                    ids.append(rid)
                    inputs.append({"id": rid, "family": family, "input": context})
                    gold.append({"id": rid, "family": family, "difficulty": ["direct", "compositional"][variant],
                                 "group": group, **oracle})
                groups.append({"split": split, "family": family, "group": group, "ids": ids})
        byid = {g["id"]: g for g in gold}
        random.Random(seeds[split] + "/shuffle").shuffle(inputs)
        outputs[split] = (inputs, [byid[r["id"]] for r in inputs])
    return outputs, groups


def check_answer(record, gold, answer):
    try:
        family, context = record["family"], record["input"]
        if family == "sql":
            if not isinstance(answer, dict) or set(answer) != {"sql"}:
                return False
            return all(sql_result(answer["sql"], db) == expected for db, expected in zip(gold["check_databases"], gold["expected_results"]))
        if family == "schedule":
            return schedule_valid(answer, context)
        if family == "workflow":
            return workflow_valid(answer, context)
        return canonical(answer) == canonical(gold["answer"])
    except (ValueError, TypeError, KeyError, sqlite3.Error, OverflowError):
        return False


def score(records, gold, predictions):
    expected = {r["id"] for r in records}
    received = [p.get("id") if isinstance(p, dict) else None for p in predictions]
    try:
        unique = set(received)
    except TypeError:
        return {"status": "unscored", "reason": "invalid response identity"}
    if len(received) != len(expected) or len(unique) != len(received) or unique != expected:
        return {"status": "unscored", "reason": "missing, duplicate, or unexpected response IDs"}
    gs, ps = {x["id"]: x for x in gold}, {x["id"]: x for x in predictions}
    if set(gs) != expected:
        return {"status": "unscored", "reason": "gold coverage mismatch"}
    correct = {f: 0 for f in FAMILIES}
    counts = {f: 0 for f in FAMILIES}
    for record in records:
        family = record["family"]
        counts[family] += 1
        correct[family] += int(check_answer(record, gs[record["id"]], ps[record["id"]].get("answer")))
    return {"status": "diagnostic_complete", "score": 100 * sum(correct.values()) / len(records),
            "correct": sum(correct.values()), "count": len(records),
            "family_accuracy": {f: correct[f] / counts[f] for f in FAMILIES},
            "official_eligibility_checked": False, "model_response_provenance_checked": False}


def paths(split):
    base = ROOT / "data" / "public"
    return base / (split + ".jsonl"), base / (split + "_gold.jsonl")
