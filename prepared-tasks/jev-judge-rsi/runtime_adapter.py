"""Explicitly unavailable model backend; no fabricated model outputs."""
class ModelRuntimeUnavailable(RuntimeError):
    pass


class FrozenModelAdapter:
    def __init__(self, *args, **kwargs):
        raise ModelRuntimeUnavailable("MODEL_RUNTIME_UNAVAILABLE: pinned JEV-27B-VL H100 inference and authentic token accounting are not integrated.")
    def decide(self, observable_bundle, prompt):
        """Return S1 completion probability and real text/image usage receipts."""
        raise ModelRuntimeUnavailable("unimplemented")
    def review(self, observable_bundle, prompt, max_tokens=382):
        """Return a bounded S2 diagnosis with thinking disabled and usage."""
        raise ModelRuntimeUnavailable("unimplemented")
