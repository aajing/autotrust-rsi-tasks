"""Strict declarative policy admission; no candidate executable inference."""
import json
import math

FEATURES = tuple([f"embedding_{i:02d}" for i in range(64)] +
                 ["confidence", "entropy", "prompt_tokens", "answer_tokens", "tool_status", "spent_tokens", "remaining_tokens", "remaining_items"])
ACTIONS = ("return", "reconsider_256", "reconsider_512", "reconsider_1024", "tool_check")


def validate_mlp(layers, input_dim, output_dim, max_parameters):
    if not isinstance(layers, list) or len(layers) != 3:
        raise ValueError("exactly two hidden layers and an output layer required")
    previous, parameters = input_dim, 0
    for index, layer in enumerate(layers):
        if not isinstance(layer, dict) or set(layer) != {"weight", "bias"}:
            raise ValueError("invalid dense layer")
        weight, bias = layer["weight"], layer["bias"]
        if not isinstance(weight, list) or not isinstance(bias, list) or len(weight) != len(bias):
            raise ValueError("weight/bias shapes")
        expected = output_dim if index == 2 else len(weight)
        if len(weight) != expected or not 1 <= len(weight) <= 128:
            raise ValueError("layer width")
        if any(not isinstance(row, list) or len(row) != previous or any(not finite(v) for v in row) for row in weight):
            raise ValueError("weight shape/nonfinite")
        if any(not finite(v) for v in bias):
            raise ValueError("nonfinite bias")
        parameters += len(weight) * (previous + 1)
        previous = len(weight)
    if parameters > max_parameters:
        raise ValueError("parameter cap")


def forward(layers, values):
    for index, layer in enumerate(layers):
        values = [sum(w*x for w, x in zip(row, values)) + bias for row, bias in zip(layer["weight"], layer["bias"])]
        if any(not math.isfinite(x) for x in values):
            raise ValueError("nonfinite MLP activation")
        if index < len(layers)-1:
            values = [max(0, x) for x in values]
    return values


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def admit(policy):
    if isinstance(policy, dict) and policy.get("kind") == "mlp":
        if set(policy) != {"version", "kind", "feature_names", "mean", "scale", "layers"} or policy["version"] != 1:
            raise ValueError("MLP schema")
        if policy["feature_names"] != list(FEATURES):
            raise ValueError("frozen feature order")
        for key in ("mean", "scale"):
            if not isinstance(policy[key], list) or len(policy[key]) != len(FEATURES) or any(not finite(x) for x in policy[key]):
                raise ValueError("feature normalization")
        if any(x <= 0 for x in policy["scale"]):
            raise ValueError("normalization scale must be positive")
        validate_mlp(policy["layers"], len(FEATURES), len(ACTIONS), 65536)
        return policy
    required = {"version", "kind", "threshold", "reconsider_tokens", "max_reconsiderations", "tool_check"}
    if not isinstance(policy, dict) or set(policy) != required or policy["version"] != 1:
        raise ValueError("unsupported policy schema")
    if policy["kind"] not in ("threshold", "fixed_reconsideration") or not finite(policy["threshold"]) or not 0 <= policy["threshold"] <= 1:
        raise ValueError("invalid threshold policy")
    if type(policy["reconsider_tokens"]) is not int or policy["reconsider_tokens"] not in (256, 512, 1024):
        raise ValueError("invalid reconsideration cap")
    if type(policy["max_reconsiderations"]) is not int or not 0 <= policy["max_reconsiderations"] <= 2:
        raise ValueError("invalid reconsideration count")
    if type(policy["tool_check"]) is not bool:
        raise ValueError("invalid tool flag")
    return policy


def choose_action(policy, features, reconsiderations=0, tool_used=False):
    admit(policy)
    if policy["kind"] in ("threshold", "fixed_reconsideration"):
        p = features["confidence"]
        if not finite(p) or not 0 <= p <= 1:
            raise ValueError("confidence bound")
        if policy["kind"] == "threshold" and p >= policy["threshold"]:
            return "return"
        if reconsiderations < policy["max_reconsiderations"]:
            return "reconsider_" + str(policy["reconsider_tokens"])
        return "tool_check" if policy["tool_check"] and not tool_used else "return"
    if any(k not in features or not finite(features[k]) for k in FEATURES):
        raise ValueError("missing/nonfinite features")
    values = [max(-10, min(10, (features[k]-m)/s)) for k, m, s in zip(FEATURES, policy["mean"], policy["scale"])]
    logits = forward(policy["layers"], values)
    return ACTIONS[max(range(len(logits)), key=lambda i: logits[i])]


class Budget:
    """Arithmetic only: a future trusted broker must provide authentic usage."""
    def __init__(self, limits):
        self.limits, self.used = dict(limits), {k: 0 for k in limits}

    def reserve(self, cost, remaining_mandatory=None):
        remaining_mandatory = remaining_mandatory or {}
        if set(cost) - set(self.limits) or any(type(v) is not int or v < 0 for v in cost.values()):
            raise ValueError("invalid budget receipt")
        if any(self.used[k] + cost.get(k, 0) + remaining_mandatory.get(k, 0) > cap for k, cap in self.limits.items()):
            return False
        for k, v in cost.items():
            self.used[k] += v
        return True
