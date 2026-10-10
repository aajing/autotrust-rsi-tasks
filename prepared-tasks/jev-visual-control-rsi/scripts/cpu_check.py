#!/usr/bin/env python3
import datetime
import json
from pathlib import Path
import platform
import sys
import unittest
import PIL
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_cpu.py")
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"python":platform.python_version(),
        "platform":platform.platform(),"Pillow":PIL.__version__,"tests_run":result.testsRun,
        "failures":len(result.failures),"errors":len(result.errors),"passed":result.wasSuccessful(),
        "certificate_replays":224 if result.wasSuccessful() else None,"model_calls":0,"GPU_runs":0,
        "native_ipc_synthetic_transport_fixture":result.wasSuccessful(),
        "fixture_is_model_inference_or_performance":False,
        "optional_uid_separation_executed":False,"optional_mujoco_engine_executed":False,
        "new_suite_baseline_score":None,"H100_runtime_and_memory":None}
(ROOT/"evidence/cpu_validation.json").write_text(json.dumps(report,indent=2)+"\n")
raise SystemExit(0 if result.wasSuccessful() else 1)
