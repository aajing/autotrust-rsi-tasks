"""Operator-owned persistent Work accounting, shared across local invocations."""
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
import re
import time


class WorkBudget:
    def __init__(self, directory, work_id):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", work_id or ""):
            raise ValueError("operator must supply a stable --work-id")
        directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
        self.path=directory/(work_id+".json")
        with self.locked() as state:
            self.start=state["started_unix"]

    @contextmanager
    def locked(self):
        with self.path.open("a+",encoding="utf-8") as f:
            fcntl.flock(f,fcntl.LOCK_EX);f.seek(0);text=f.read()
            state=json.loads(text) if text else {"started_unix":time.time(),"calls":0,"new_episodes":0}
            if time.time()-state["started_unix"]>=7200:raise ValueError("Work 2-hour budget exhausted")
            yield state
            f.seek(0);f.truncate();json.dump(state,f);f.flush()

    def charge_call(self):
        with self.locked() as state:
            if state["calls"]>=20000:raise ValueError("Work 20,000-call budget exhausted")
            state["calls"]+=1

    def charge_new_episode(self):
        with self.locked() as state:
            if state["new_episodes"]>=160:raise ValueError("Work 160-new-episode budget exhausted")
            index=state["new_episodes"];state["new_episodes"]+=1
            return index

    @property
    def remaining_seconds(self):
        return max(0.,7200-(time.time()-self.start))
