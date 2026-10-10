"""Public protocol constants. No scene data or privileged coordinates."""
import hashlib
import json
import math

FAMILIES = ("distractor_pick_place", "precision_place", "obstacle_transport", "ordered_two_place")
TIERS = ("hard", "harder")
COUNTS = {"train": 16, "development": 6, "evaluation": 6}
BOUNDS = ((-.38, .38), (-.30, .30), (.055, .32))
MAX_STEPS, DT, STEP_SECONDS = 120, .002, .5
MAX_CALLS_STEP, MAX_MEMORY_BYTES = 2, 65536
ACTION_KEYS = {"dx", "dy", "dz", "grip"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def validate_action(action):
    if not isinstance(action, dict) or set(action) != ACTION_KEYS:
        raise ValueError("action requires exactly dx,dy,dz,grip")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in action.values()):
        raise ValueError("action numbers must be finite and non-Boolean")
    if any(abs(action[k]) > .04 + 1e-10 for k in ("dx", "dy", "dz")):
        raise ValueError("displacement exceeds 0.04m")
    if not 0 <= action["grip"] <= 1:
        raise ValueError("grip must be in [0,1]")
    return {k: float(v) for k, v in action.items()}


def score_events(events, expected):
    """Task-computed scoring: exact manifest coverage, not candidate declarations."""
    expected = {r["id"]: r for r in expected}
    if len(events) != 48 or len(expected) != 48:
        raise ValueError("official Judge requires exactly 48 episodes")
    if len({r.get("id") for r in events}) != 48 or set(r.get("id") for r in events) != set(expected):
        raise ValueError("episode coverage differs from manifest")
    cells = {f + "/" + t: [] for f in FAMILIES for t in TIERS}
    for event in events:
        ref = expected[event["id"]]
        if event.get("status") != "completed" or type(event.get("success")) is not bool:
            raise ValueError("invalid/crashed/incomplete episodes are unscored")
        if event.get("family") != ref["family"] or event.get("tier") != ref["tier"]:
            raise ValueError("episode cell differs from manifest")
        if type(event.get("steps")) is not int or not 0 <= event["steps"] <= MAX_STEPS:
            raise ValueError("invalid step accounting")
        cells[ref["family"] + "/" + ref["tier"]].append(int(event["success"]))
    if any(len(v) != 6 for v in cells.values()):
        raise ValueError("Judge requires six episodes per cell")
    return {"status": "scored", "score": 100 * sum(sum(v) for v in cells.values()) / 48,
            "completed": 48, "cell_success": {k: sum(v) / 6 for k, v in cells.items()}}
