"""Public deterministic scenes; the running controller receives observations only."""
import hashlib
import hmac
import random
from .contract import FAMILIES, TIERS, sha


def seed_for(master, split, family, tier, attempt):
    msg = f"visual-control-v1/{split}/{family}/{tier}/{attempt}".encode()
    return int.from_bytes(hmac.new(bytes.fromhex(master), msg, hashlib.sha256).digest()[:8], "big")


def geometry(record):
    return {k: record[k] for k in ("family", "tier", "objects", "trays", "goals", "obstacles", "initial_gripper")}


def make_scene(family, tier, seed):
    if family not in FAMILIES or tier not in TIERS:
        raise ValueError("unknown family/tier")
    r = random.Random(seed)
    n = 4 if tier == "hard" else 6
    # Targets, distractors, and trays occupy separate slots with seed-dependent
    # jitter. Corridors remain feasible, but images and precision vary.
    slots = [(-.21, -.09), (-.23, .09), (-.10, -.21), (.08, -.22), (-.12, .21), (.10, .21)]
    descriptions = ["blue striped block", "red dotted cylinder", "blue dotted block",
                    "red striped block", "blue plain cylinder", "red plain cylinder"]
    colors = ["#376cca", "#c55051", "#456bc5", "#c85d60", "#4773c4", "#cb6265"]
    objects = []
    for i in range(n):
        x, y = slots[i]
        half = .018
        objects.append({"id": f"object-{i}", "description": descriptions[i],
                        "shape": "cylinder" if "cylinder" in descriptions[i] else "box",
                        "pattern": "stripe" if "striped" in descriptions[i] else "dots" if "dotted" in descriptions[i] else "plain",
                        "color": colors[i], "half": half,
                        "position": [round(x + r.uniform(-.016, .016), 5), round(y + r.uniform(-.016, .016), 5), half]})
    precise = family == "precision_place"
    half = (.025 if tier == "hard" else .022) if precise else .058
    trays = [{"id": "tray-0", "description": "yellow tray", "color": "#e1bc49",
              "position": [round(.23 + r.uniform(-.022, .022), 5), round(-.085 + r.uniform(-.02, .02), 5)],
              "half": half}]
    if family == "ordered_two_place":
        trays.append({"id": "tray-1", "description": "green tray", "color": "#5ba46c",
                      "position": [round(.22 + r.uniform(-.02, .02), 5), round(.115 + r.uniform(-.02, .02), 5)], "half": .058})
    goals = [{"object": "object-0", "tray": "tray-0", "tolerance": (.006 if tier == "hard" else .003) if precise else None}]
    if family == "ordered_two_place":
        goals.append({"object": "object-1", "tray": "tray-1", "tolerance": None})
    obstacles = []
    if family == "obstacle_transport":
        obstacles = [{"id": "barrier", "min": [-.035, -.10, 0.0], "max": [.035, .105, .38], "color": "#686476"}]
    record = {"schema": 1, "family": family, "tier": tier, "seed": seed,
              "objects": objects, "trays": trays, "goals": goals, "obstacles": obstacles,
              "initial_gripper": [-.28, -.10, .24], "delay_steps": 1 if tier == "hard" else 2,
              "appearance": {"brightness": round(r.uniform(.82, 1.13), 3), "grid_offset": r.randrange(16),
                             "occluded_view": r.choice(["top", "oblique"]), "occluder_fraction": .20 if tier == "hard" else .32}}
    record["geometry_sha256"] = sha(geometry(record))
    record["id"] = "scene-" + record["geometry_sha256"][:20]
    return record
