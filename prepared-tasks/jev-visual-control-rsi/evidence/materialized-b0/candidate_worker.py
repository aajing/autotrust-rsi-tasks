"""Observation-only JSONL worker; OS permissions remain operator responsibility."""
import importlib.util
import json
import sys


def read():
    line = sys.stdin.readline(2000001)
    if not line or len(line) > 2000000: raise ValueError("missing/oversized IPC input")
    return json.loads(line)


def send(value):
    print(json.dumps(value, allow_nan=False, separators=(",", ":")), flush=True)


class ModelProxy:
    def decide(self, payload):
        send({"kind": "model_request", "payload": payload})
        msg = read()
        if msg.get("kind") != "model_response": raise ValueError("broker refused request")
        return msg["result"]


def main():
    spec = importlib.util.spec_from_file_location("candidate", sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    controller = module.Controller(ModelProxy())
    while True:
        message = read()
        if message["kind"] == "stop": break
        if message["kind"] == "reset":
            controller.reset()
            send({"kind": "ready"})
        elif message["kind"] == "step":
            action = controller.step(message["observation"])
            memory = controller.memory()
            if len(json.dumps(memory, allow_nan=False).encode()) > 65536: raise ValueError("memory exceeds 64 KiB")
            send({"kind": "action", "action": action, "memory_bytes": len(json.dumps(memory).encode())})
        else: raise ValueError("unknown command")


if __name__ == "__main__": main()
