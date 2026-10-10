"""Fail-closed model boundary. Installing a backend is task integration work."""
class ModelRuntimeUnavailable(RuntimeError):
    pass


class FrozenModelAdapter:
    def __init__(self, *args, **kwargs):
        raise ModelRuntimeUnavailable(
            "MODEL_RUNTIME_UNAVAILABLE: no validated GEV H100 backend is packaged; "
            "CPU diagnostic scores must not be represented as model results.")

    def generate(self, messages, max_output_tokens, thinking=False):
        """Backend must return text plus actual prompt/completion token receipts."""
        raise ModelRuntimeUnavailable("unimplemented")

    def verify(self, task_input, candidate_answer):
        """Backend must use pinned S1 and calibration_gold.json, with usage."""
        raise ModelRuntimeUnavailable("unimplemented")
