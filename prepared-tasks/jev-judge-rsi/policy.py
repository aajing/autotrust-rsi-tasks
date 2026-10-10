"""Baseline policy schema and bounded affine probability calibration."""
import math

FEATURES = ("initial_probability", "review_probability", "text_length", "image_count")


def valid_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_layers(layers):
    if not isinstance(layers, list) or len(layers) != 3:
        raise ValueError("two hidden layers plus output required")
    previous, parameters = 4, 0
    for index, layer in enumerate(layers):
        if not isinstance(layer, dict) or set(layer) != {"weight", "bias"}:
            raise ValueError("layer schema")
        weights, bias = layer["weight"], layer["bias"]
        if not isinstance(weights, list) or not isinstance(bias, list) or len(weights) != len(bias) or not 1 <= len(weights) <= 64:
            raise ValueError("layer shape")
        if index == 2 and len(weights) != 1:
            raise ValueError("scalar probability output required")
        if any(not isinstance(row, list) or len(row) != previous or any(not valid_number(x) for x in row) for row in weights) or any(not valid_number(x) for x in bias):
            raise ValueError("nonfinite/shape error")
        parameters += len(weights)*(previous+1); previous = len(weights)
    if parameters > 16384:
        raise ValueError("parameter cap")


def admit(policy):
    if not isinstance(policy, dict) or set(policy) != {"version", "prompt", "use_s2_review", "use_s1_recheck", "calibration"}:
        raise ValueError("policy schema")
    if policy["version"] != 1 or not isinstance(policy["prompt"], str) or len(policy["prompt"]) > 8192:
        raise ValueError("version/prompt bound")
    if type(policy["use_s2_review"]) is not bool or type(policy["use_s1_recheck"]) is not bool:
        raise ValueError("invalid call graph flags")
    if policy["use_s1_recheck"] and not policy["use_s2_review"]:
        raise ValueError("recheck requires review")
    c = policy["calibration"]
    if isinstance(c, dict) and c.get("kind") == "mlp_clip":
        if set(c) != {"kind", "feature_names", "layers"} or c["feature_names"] != list(FEATURES):
            raise ValueError("MLP calibration schema")
        validate_layers(c["layers"])
    else:
        if not isinstance(c, dict) or set(c) != {"kind", "a", "b"} or c["kind"] != "affine_clip":
            raise ValueError("unsupported calibrator")
        if any(not valid_number(c[k]) or abs(c[k]) > 100 for k in ("a", "b")):
            raise ValueError("calibration bounds")
    return policy


def calibrate(p, config, features=None):
    if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("invalid model probability")
    if config["kind"] == "affine_clip":
        return max(0.0, min(1.0, config["a"]*p+config["b"]))
    validate_layers(config["layers"])
    features = features or {"initial_probability":p, "review_probability":p, "text_length":0, "image_count":0}
    if any(k not in features or not valid_number(features[k]) for k in FEATURES):
        raise ValueError("calibration features")
    values = [features[FEATURES[0]], features[FEATURES[1]], min(features[FEATURES[2]], 3000)/3000, min(features[FEATURES[3]], 2)/2]
    for index, layer in enumerate(config["layers"]):
        values = [sum(w*x for w,x in zip(row, values))+b for row,b in zip(layer["weight"],layer["bias"])]
        if any(not math.isfinite(x) for x in values): raise ValueError("nonfinite MLP output")
        if index < 2: values = [max(0,x) for x in values]
    return max(0.0, min(1.0, values[0]))


class Budget:
    """Receipt arithmetic only; genuine usage must come from a trusted broker."""
    def __init__(self, limits):
        self.limits, self.used = dict(limits), {k: 0 for k in limits}
    def reserve(self, cost, mandatory=None):
        mandatory = mandatory or {}
        if set(cost)-set(self.limits) or any(type(v) is not int or v < 0 for v in cost.values()):
            raise ValueError("invalid cost")
        if any(self.used[k]+cost.get(k, 0)+mandatory.get(k, 0) > cap for k, cap in self.limits.items()):
            return False
        for k, v in cost.items(): self.used[k] += v
        return True
