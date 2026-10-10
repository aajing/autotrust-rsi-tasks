"""Deterministic CPU kinematic surrogate, not a rigid-body robot simulator.

Truth remains in this owner process. observation() is the only actor interface.
Attachment is geometric; released objects settle vertically under gravity.
Collision uses swept samples no more than 0.277 mm apart per 2-ms tick.
"""
import base64
import copy
import io
import math
from collections import deque
from PIL import Image, ImageDraw, ImageEnhance
from .contract import BOUNDS, DT, MAX_STEPS, STEP_SECONDS, validate_action


def norm(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def overlap(center, radius, box):
    return all(center[i] + radius > box["min"][i] and center[i] - radius < box["max"][i] for i in range(3))


class Environment:
    def __init__(self, record):
        self.record = copy.deepcopy(record)
        self.objects = {o["id"]: copy.deepcopy(o) for o in record["objects"]}
        self.initial = {o["id"]: list(o["position"]) for o in record["objects"]}
        self.trays = {t["id"]: t for t in record["trays"]}
        self.goals = record["goals"]
        self.gripper = list(record["initial_gripper"])
        self.grip = 1.0
        self.held = None
        self.vertical_velocity = {k: 0.0 for k in self.objects}
        self.completed = [False] * len(self.goals)
        self.stable = [0.0] * len(self.goals)
        self.steps = 0
        self.time = 0.0
        self.done = self.success = False
        self.invalid = False
        self.reason = "running"
        self.previous_action = None
        self.history = deque(maxlen=4)
        self.history.append(self._snapshot())

    def _snapshot(self):
        return {"step": self.steps, "objects": copy.deepcopy(list(self.objects.values())),
                "gripper": list(self.gripper), "grip": self.grip}

    @property
    def goal(self):
        parts = [f"place the {self.objects[g['object']]['description']} in the {self.trays[g['tray']]['description']}" for g in self.goals]
        return "Then ".join(p.capitalize() + ". " for p in parts).strip() + " Avoid barriers and do not disturb other objects."

    def _end(self, reason, success=False, invalid=False):
        self.done, self.success, self.invalid, self.reason = True, success, invalid, reason

    def _goal_ok(self, i):
        g = self.goals[i]
        obj, tray = self.objects[g["object"]], self.trays[g["tray"]]
        p, q, h = obj["position"], tray["position"], obj["half"]
        inside = all(abs(p[j] - q[j]) + h <= tray["half"] + 1e-9 for j in (0, 1))
        precise = g["tolerance"] is None or math.hypot(p[0]-q[0], p[1]-q[1]) <= g["tolerance"] + 1e-9
        return self.held != obj["id"] and inside and precise and abs(p[2] - (h + .006)) < 1e-7 and abs(self.vertical_velocity[obj["id"]]) < 1e-9

    def _floor(self, obj):
        p, h = obj["position"], obj["half"]
        if any(all(abs(p[j]-t["position"][j]) + h <= t["half"] + 1e-9 for j in (0, 1)) for t in self.trays.values()):
            return h + .006
        return h

    def _collision(self):
        if any(not (a + .015 <= p <= b - .015) for p, (a, b) in zip(self.gripper[:2], BOUNDS[:2])):
            return "workspace_collision"
        if not BOUNDS[2][0] <= self.gripper[2] <= BOUNDS[2][1]:
            return "workspace_collision"
        for barrier in self.record["obstacles"]:
            if overlap(self.gripper, .015, barrier):
                return "barrier_collision"
        if self.held:
            obj = self.objects[self.held]
            p, h = obj["position"], obj["half"]
            if p[2] < h - 1e-9:
                return "table_collision"
            if any(overlap(p, h, b) for b in self.record["obstacles"]):
                return "carried_object_collision"
            for other in self.objects.values():
                if other["id"] != self.held and all(abs(p[i]-other["position"][i]) < h + other["half"] - 1e-8 for i in range(3)):
                    return "object_collision"
        targets = {g["object"] for g in self.goals}
        if any(k not in targets and norm(v["position"], self.initial[k]) > .015 + 1e-9 for k, v in self.objects.items()):
            return "non_target_displacement"
        return None

    def step(self, action):
        if self.done:
            return {"valid": not self.invalid, "terminal": True, "success": self.success, "reason": self.reason}
        try:
            a = validate_action(action)
        except (ValueError, TypeError):
            self._end("candidate_invalid_action", invalid=True)
            return {"valid": False, "terminal": True, "success": False, "reason": self.reason}
        self.steps += 1
        start = list(self.gripper)
        end = [start[i] + a[k] for i, k in enumerate(("dx", "dy", "dz"))]
        # Changing aperture happens at the endpoint, so translate-then-grasp is
        # deterministic and cannot attach to an object crossed mid-sweep.
        for tick in range(round(STEP_SECONDS / DT)):
            fraction = (tick + 1) / round(STEP_SECONDS / DT)
            self.gripper = [start[i] + (end[i]-start[i])*fraction for i in range(3)]
            if self.held:
                self.objects[self.held]["position"] = [self.gripper[0], self.gripper[1], self.gripper[2]-.045]
            for key, obj in self.objects.items():
                if key == self.held:
                    continue
                floor = self._floor(obj)
                if obj["position"][2] > floor:
                    self.vertical_velocity[key] -= 9.81*DT
                    obj["position"][2] = max(floor, obj["position"][2] + self.vertical_velocity[key]*DT)
                    if obj["position"][2] <= floor:
                        self.vertical_velocity[key] = 0.0
            self.time += DT
            collision = self._collision()
            if collision:
                self._end(collision)
                break
            for i in range(len(self.goals)):
                self.stable[i] = self.stable[i] + DT if self._goal_ok(i) else 0.0
                if self.stable[i] >= .5 - 1e-9:
                    self.completed[i] = True
            if all(self._goal_ok(i) and self.stable[i] >= .5-1e-9 for i in range(len(self.goals))):
                self._end("success", success=True)
                break
        released = None
        if not self.done:
            if a["grip"] <= .2 and self.grip > .2 and self.held is None:
                near = [o for o in self.objects.values() if math.hypot(o["position"][0]-self.gripper[0], o["position"][1]-self.gripper[1]) <= .012
                        and abs(o["position"][2]-(self.gripper[2]-.045)) <= .012]
                if not near:
                    self._end("missed_grasp")
                else:
                    near.sort(key=lambda o: (norm(o["position"], [*self.gripper[:2], self.gripper[2]-.045]), o["id"]))
                    chosen = near[0]["id"]
                    goal_index = next((i for i, g in enumerate(self.goals) if g["object"] == chosen), None)
                    if goal_index is not None and not all(self.completed[:goal_index]):
                        self._end("order_violation")
                    else:
                        self.held = chosen
                        self.vertical_velocity[chosen] = 0.0
            if a["grip"] >= .8 and self.held is not None:
                released, self.held = self.held, None
                self.vertical_velocity[released] = 0.0
            self.grip = a["grip"]
        # Wrong release is an ordinary failed episode, not a malformed action.
        if released and not self.done:
            match = next((g for g in self.goals if g["object"] == released), None)
            if match:
                obj, tray = self.objects[released], self.trays[match["tray"]]
                p, q = obj["position"], tray["position"]
                if any(abs(p[i]-q[i])+obj["half"] > tray["half"]+1e-9 for i in (0, 1)):
                    self._end("wrong_placement")
        self.previous_action = a
        if not self.done and self.steps >= MAX_STEPS:
            self._end("step_exhaustion")
        if not self.done and self.time >= 90:
            self._end("simulation_time_exhaustion")
        self.history.append(self._snapshot())
        return {"valid": not self.invalid, "terminal": self.done, "success": self.success, "reason": self.reason}

    @staticmethod
    def project(position, view):
        x, y, z = position
        if view == "top":
            return 192 + x*450, 192-y*500
        return 192+x*450, 215-y*230-z*330

    def render(self, view="top", snapshot=None, occlusion=True):
        if view not in ("top", "oblique"):
            raise ValueError("unknown camera")
        s = snapshot or self._snapshot()
        im = Image.new("RGB", (384, 384), "#bbb5a7")
        d = ImageDraw.Draw(im)
        offset = self.record["appearance"]["grid_offset"]
        for k in range(offset, 384, 24):
            d.line((k, 0, k, 384), fill="#b0ab9f")
            d.line((0, k, 384, k), fill="#b0ab9f")
        for tray in self.trays.values():
            x, y = self.project([*tray["position"], .006], view)
            hx, hy = tray["half"]*450, tray["half"]*(500 if view == "top" else 230)
            d.rectangle((x-hx, y-hy, x+hx, y+hy), fill=tray["color"], outline="#37352d", width=3)
        for b in self.record["obstacles"]:
            points = [self.project([x, y, b["max"][2] if view == "oblique" else 0], view)
                      for x, y in [(b["min"][0], b["min"][1]), (b["max"][0], b["min"][1]),
                                   (b["max"][0], b["max"][1]), (b["min"][0], b["max"][1])]]
            if view == "oblique":
                lower = [self.project([x, y, 0], view) for x,y in [(b["max"][0], b["min"][1]), (b["min"][0], b["min"][1])]]
                d.polygon(points[:2]+lower, fill="#55505f")
            d.polygon(points, fill=b["color"], outline="#272631")
        for obj in sorted(s["objects"], key=lambda o: (-o["position"][1], o["position"][2])):
            x, y = self.project(obj["position"], view)
            hx, hy = obj["half"]*450, obj["half"]*(500 if view == "top" else 390)
            box=(x-hx,y-hy,x+hx,y+hy)
            (d.ellipse if obj["shape"] == "cylinder" else d.rectangle)(box, fill=obj["color"], outline="#242632", width=1)
            if obj["pattern"] == "stripe":
                for delta in (-4, 2): d.line((x+delta,y-hy+2,x+delta,y+hy-2), fill="#dddfe2", width=2)
            elif obj["pattern"] == "dots":
                for dx,dy in [(-3,-3),(3,3)]: d.ellipse((x+dx-1,y+dy-1,x+dx+1,y+dy+1),fill="#dddfe2")
        gx, gy = self.project(s["gripper"], view)
        if view == "top":
            d.ellipse((gx-3,gy-3,gx+3,gy+3),fill="black")
        else:
            gap=4+8*s["grip"]
            d.rectangle((gx-gap-3,gy-8,gx-gap,gy+8),fill="#2c2c30")
            d.rectangle((gx+gap,gy-8,gx+gap+3,gy+8),fill="#2c2c30")
            d.line((gx-gap-3,gy-8,gx+gap+3,gy-8),fill="#36363c",width=4)
        if occlusion and view == self.record["appearance"]["occluded_view"]:
            # The other view is never overlaid. A partial stripe masks a region
            # of the first target, not an entire scene or a privileged mask.
            target = next(o for o in s["objects"] if o["id"] == self.goals[0]["object"])
            x,y = self.project(target["position"],view)
            width=4 if self.record["tier"]=="hard" else 7
            d.rectangle((x-width,y-16,x+width,y+16),fill="#777a77")
        return ImageEnhance.Brightness(im).enhance(self.record["appearance"]["brightness"])

    def observation(self):
        wanted=max(0,self.steps-self.record["delay_steps"])
        snapshot=next(s for s in self.history if s["step"]==wanted)
        images={}
        for view in ("top", "oblique"):
            stream=io.BytesIO();self.render(view,snapshot).save(stream,format="PNG")
            images[view]="data:image/png;base64,"+base64.b64encode(stream.getvalue()).decode()
        return {"goal": self.goal, "placements": [{"object": self.objects[g["object"]]["description"], "destination": self.trays[g["tray"]]["description"]} for g in self.goals],
                "images": images, "image_age_steps": self.steps-snapshot["step"],
                "proprioception": {"position": list(self.gripper), "grip": self.grip},
                "previous_action": self.previous_action, "remaining_steps": MAX_STEPS-self.steps,
                "calibration": {"projection": "orthographic", "image_size": [384,384],
                                "top": {"origin_px": [192,192], "x_px_per_m":450, "y_px_per_m":-500},
                                "oblique": {"origin_px":[192,215],"x_px_per_m":450,"y_px_per_m":-230,"z_px_per_m":-330},
                                "workspace_bounds": BOUNDS, "carry_z": .24, "grasp_offset_z": .045}}

    def event(self):
        return {"id":self.record["id"],"family":self.record["family"],"tier":self.record["tier"],
                "status":"candidate_invalid" if self.invalid else "completed" if self.done else "incomplete",
                "success":self.success,"reason":self.reason,"steps":self.steps,"simulation_seconds":round(self.time,6)}
