"""Source-inspired B0: visual directional probabilities + phased servo.

This is candidate code. It imports no scene/environment/oracle information.
Its performance on the new suite has NOT been measured.
"""
import json


class Controller:
    def __init__(self, model):
        self.model = model
        self.reset()

    def reset(self):
        self.goal_index = 0
        self.phase = "align_object"
        self.gains = [.04, .04]
        self.last_sign = [0, 0]
        self.phase_steps = self.waits = 0

    def memory(self):
        return {"goal_index": self.goal_index, "phase": self.phase, "gains": self.gains,
                "last_sign": self.last_sign, "phase_steps": self.phase_steps, "waits": self.waits}

    def ask(self, obs, question, options):
        state = [obs["goal"], "Delayed top view:", {"image": obs["images"]["top"]},
                 "Delayed oblique view:", {"image": obs["images"]["oblique"]},
                 "Current own gripper state and image age: " + json.dumps({"proprioception": obs["proprioception"], "age": obs["image_age_steps"]})]
        return self.model.decide({"kind": "choice", "state": state, "question": question,
                                  "options": options, "thinking": "off"})["probabilities"]

    def enter(self, phase):
        self.phase, self.phase_steps = phase, 0
        self.gains, self.last_sign = [.04, .04], [0, 0]

    def step(self, obs):
        own = obs["proprioception"]
        a = {"dx": 0., "dy": 0., "dz": 0., "grip": own["grip"]}
        placement = obs["placements"][min(self.goal_index, len(obs["placements"])-1)]
        self.phase_steps += 1
        if self.phase in ("align_object", "align_tray"):
            target = placement["object"] if self.phase == "align_object" else placement["destination"]
            signs = []
            for axis, labels in enumerate((["left", "right"], ["below", "above"])):
                p = self.ask(obs, f"In the top view, is the center of the {target} {labels[0]} or {labels[1]} of the black gripper dot?", labels)
                sign = 1 if p[1] >= p[0] else -1
                self.gains[axis] = max(.0025, self.gains[axis]*.5) if self.last_sign[axis] and sign != self.last_sign[axis] else min(.04, self.gains[axis]*1.05)
                self.last_sign[axis] = sign
                signs.append(sign)
            a["dx"], a["dy"] = [s*g for s,g in zip(signs, self.gains)]
            if max(self.gains) <= .005 or self.phase_steps >= 28:
                a["dx"] = a["dy"] = 0.
                self.enter("lower_object" if self.phase == "align_object" else "lower_tray")
        else:
            # Source adaptation uses one visual check even on scripted z/aperture
            # phases, preserving the shared one-request minimum per step.
            self.ask(obs, f"Is the gripper visually ready for phase {self.phase}?", ["no", "yes"])
            if self.phase in ("lower_object", "lift", "lower_tray"):
                target_z = {"lower_object": .063, "lift": .24, "lower_tray": .085}[self.phase]
                a["dz"] = max(-.04, min(.04, target_z-own["position"][2]))
                if abs(target_z-own["position"][2]) <= .04:
                    self.enter({"lower_object": "close", "lift": "align_tray", "lower_tray": "release"}[self.phase])
            elif self.phase == "close":
                a["grip"] = 0.
                self.enter("lift")
            elif self.phase == "release":
                a["grip"] = 1.
                self.enter("settle")
            elif self.phase == "settle" and self.phase_steps >= 2:
                self.goal_index += 1
                if self.goal_index < len(obs["placements"]): self.enter("raise_next")
            elif self.phase == "raise_next":
                a["dz"] = max(0., min(.04, .24-own["position"][2]))
                if .24-own["position"][2] <= .04: self.enter("align_object")
        return a
