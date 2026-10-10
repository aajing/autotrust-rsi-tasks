"""Native single-container observation IPC and exact-coverage scoring.

Public data is inspectable. A scored controller must follow the observation-only
method contract; this subprocess is not an arbitrary-root security boundary.
An optional different-UID launch provides ordinary filesystem separation.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import selectors
import shutil
import subprocess
import sys
import time
from .contract import score_events
from .environment import Environment
from .model_client import ModelClient
from .budget import WorkBudget


def claim_attempt(path):
    """Charge controls, failed admission, crashes and timeouts before execution."""
    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        lines = [line for line in f if line.strip()]
        if len(lines) >= 12: raise ValueError("12 attempted Judge calls exhausted")
        f.write(json.dumps({"attempt": len(lines)+1, "started_unix": time.time()})+"\n")
        f.flush(); os.fsync(f.fileno())


def worker_command(work, owner_data, worker_user=None):
    work = Path(work).resolve()
    expected_worker = Path(__file__).with_name("candidate_worker.py").read_bytes()
    if not (work/"candidate_worker.py").is_file() or (work/"candidate_worker.py").read_bytes() != expected_worker:
        raise ValueError("candidate worker differs from owner-frozen transport")
    command = [sys.executable, "-I", str(work/"candidate_worker.py"), str(work/"controller.py")]
    if worker_user:
        if sys.platform != "linux" or os.geteuid() != 0:
            raise ValueError("optional worker-user launch requires Linux root; omit it for native IPC")
        user = pwd.getpwnam(worker_user)
        if user.pw_uid == 0 or not shutil.which("setpriv"):
            raise ValueError("optional UID separation needs a non-root worker and setpriv")
        st = Path(owner_data).stat()
        if st.st_uid != 0 or st.st_mode & 0o077:
            raise ValueError("owner data directory must be root-owned mode 0700")
        command = ["setpriv", f"--reuid={user.pw_uid}",
                   f"--regid={user.pw_gid}", "--clear-groups", "--no-new-privs", "--"] + command
    return command


class Worker:
    def __init__(self, command, cwd, deadline):
        self.deadline = deadline
        self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, bufsize=0,
                                        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"})
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = bytearray()

    def send(self, value):
        self.process.stdin.write(json.dumps(value, allow_nan=False).encode()+b"\n")
        self.process.stdin.flush()

    def read(self):
        while b"\n" not in self.buffer:
            remain = min(120., self.deadline-time.monotonic())
            if remain <= 0 or not self.selector.select(remain): raise TimeoutError("worker/global timeout")
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk: raise ValueError("worker exited without complete result")
            self.buffer.extend(chunk)
            if len(self.buffer) > 2000000: raise ValueError("worker IPC message too large")
        line, _, self.buffer = self.buffer.partition(b"\n")
        return json.loads(line)

    def close(self):
        with contextlib.suppress(Exception): self.process.kill()
        with contextlib.suppress(Exception): self.process.wait(timeout=5)
        self.selector.close()


def run_episode(record, command, cwd, broker):
    env = Environment(record)
    worker = Worker(command, cwd, broker.deadline)
    start_calls = broker.calls
    actions = []
    try:
        worker.send({"kind": "reset"})
        if worker.read() != {"kind": "ready"}: raise ValueError("invalid reset response")
        while not env.done:
            if time.monotonic() >= broker.deadline: raise TimeoutError("global time budget")
            worker.send({"kind": "step", "observation": env.observation()})
            count = 0
            while True:
                msg = worker.read()
                if msg.get("kind") == "model_request":
                    count += 1
                    if count > 2 or broker.calls-start_calls >= 240: raise ValueError("per-step/episode model cap")
                    result = broker.decide(msg["payload"])
                    worker.send({"kind": "model_response", "result": result})
                elif msg.get("kind") == "action":
                    if count < 1 or type(msg.get("memory_bytes")) is not int or not 0 <= msg["memory_bytes"] <= 65536:
                        raise ValueError("missing visual call or invalid memory accounting")
                    env.step(msg["action"])
                    actions.append(msg["action"])
                    if env.invalid: raise ValueError("candidate action invalid")
                    break
                else: raise ValueError("invalid worker message")
        event = env.event()
        event["model_calls"] = broker.calls-start_calls
        event["actions"] = actions
        return event
    finally:
        worker.close()  # new process every episode; no implicit cache persistence


def evaluate(root, work, endpoint, split="evaluation", worker_user=None, work_id=None):
    root = Path(root).resolve()
    start = time.monotonic()
    if split == "evaluation": claim_attempt(root/"data"/"judge_attempts.jsonl")
    budget = None if split=="evaluation" else WorkBudget(root/"data/work_ledgers", work_id)
    command = worker_command(work, root/"data", worker_user)
    rel = f"data/{split}/scenes.jsonl"
    manifest = json.loads((root/"data/manifest.json").read_text())
    raw = (root/rel).read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["files"][rel]["sha256"]:
        raise ValueError("frozen scene hash mismatch")
    records = [json.loads(x) for x in raw.splitlines()]
    broker = ModelClient(endpoint, start+(5400 if split=="evaluation" else budget.remaining_seconds),
                         11520 if split=="evaluation" else 20000, None if budget is None else budget.charge_call)
    events = []
    for record in records:
        events.append(run_episode(record, command, str(Path(work).resolve()), broker))
    reward = score_events(events, records) if split=="evaluation" else {"status":"development_only", "episodes":len(events), "successes":sum(e["success"] for e in events)}
    # Published per-episode diagnostics are audit evidence, open audit feedback.
    reward.update({"model_calls":broker.calls,"wall_seconds":time.monotonic()-start,
                   "collision_count":sum("collision" in e["reason"] for e in events),
                   "step_exhaustion_count":sum(e["reason"]=="step_exhaustion" for e in events),
                   "median_steps":sorted(e["steps"] for e in events)[len(events)//2],
                   "events":events,"evaluation_data_public":True,
                   "execution_lane":"optional_uid_ipc" if worker_user else "native_single_container_ipc"})
    return reward
