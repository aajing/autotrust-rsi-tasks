"""Owner-side loopback native JEV broker. No synthetic model responses."""
import base64
import io
import json
import math
import time
import urllib.parse
import urllib.request
from PIL import Image


class ModelClient:
    def __init__(self, endpoint, deadline, max_calls=11520, charge_call=None):
        url = urllib.parse.urlparse(endpoint)
        if url.scheme != "http" or url.hostname not in ("127.0.0.1", "localhost", "::1") or url.path != "/v1/decide":
            raise ValueError("endpoint must be loopback HTTP /v1/decide")
        self.endpoint, self.deadline, self.max_calls = endpoint, deadline, max_calls
        self.calls = self.prompt_tokens = 0
        self.charge_call = charge_call
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def decide(self, payload):
        if time.monotonic() >= self.deadline or self.calls >= self.max_calls:
            raise ValueError("model/global budget exhausted")
        if not isinstance(payload, dict) or set(payload) != {"kind", "state", "question", "options", "thinking"}:
            raise ValueError("restricted native request schema")
        if payload["kind"] not in ("choice", "noul", "score") or payload["thinking"] != "off":
            raise ValueError("only native System 1 probabilities allowed")
        opts = payload["options"]
        if payload["kind"] == "choice":
            if not isinstance(opts, list) or not 2 <= len(opts) <= 16 or any(not isinstance(x, str) or len(x) > 512 for x in opts):
                raise ValueError("2..16 native short options required")
        else:
            if opts is not None: raise ValueError("noul/score options must be null")
            opts = ["false", "true"] if payload["kind"] == "noul" else [str(i) for i in range(6)]
        if not isinstance(payload["question"], str) or len(payload["question"]) > 12000:
            raise ValueError("invalid question")
        state = payload["state"]
        if not isinstance(state, list) or len(state) > 20:
            raise ValueError("state must be bounded text/image parts")
        count = 0
        for part in state:
            if isinstance(part, str):
                if len(part) > 12000: raise ValueError("text part too long")
            elif isinstance(part, dict) and set(part) == {"image"}:
                value = part["image"]
                if not isinstance(value, str) or not value.startswith("data:image/png;base64,") or len(value) > 1000000:
                    raise ValueError("only bounded inline PNG images allowed")
                im = Image.open(io.BytesIO(base64.b64decode(value.split(",", 1)[1], validate=True)))
                if im.format != "PNG" or not all(1 <= n <= 384 for n in im.size):
                    raise ValueError("image exceeds 384 x 384")
                count += 1
            else:
                raise ValueError("invalid state part")
        if not 1 <= count <= 4:
            raise ValueError("each request requires 1..4 images")
        if self.charge_call: self.charge_call()
        self.calls += 1  # failed attempts are charged too
        request = dict(payload, strategy="single", system2_only=False)
        data = json.dumps(request, allow_nan=False).encode()
        req = urllib.request.Request(self.endpoint, data=data, headers={"Content-Type": "application/json"})
        with self.opener.open(req, timeout=max(.01, min(120, self.deadline-time.monotonic()))) as response:
            raw = response.read(2000001)
        if len(raw) > 2000000: raise ValueError("oversized model response")
        result = json.loads(raw)
        p = result.get("probabilities")
        if not isinstance(p, list) or len(p) != len(opts) or any(type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 1 for v in p) or abs(sum(p)-1) > 1e-4:
            raise ValueError("malformed JEV probabilities")
        tokens = result.get("usage", {}).get("prompt_tokens")
        if type(tokens) is not int or not 0 <= tokens <= 4096 or result.get("num_model_requests") != 1:
            raise ValueError("native request/token budget violation")
        if result.get("thinking", {}).get("used") is True:
            raise ValueError("System 2 is prohibited")
        self.prompt_tokens += tokens
        return {"probabilities": p, "options": opts}
