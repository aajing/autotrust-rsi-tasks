#!/usr/bin/env python3
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.task import build
if __name__=='__main__': print(json.dumps(build(),indent=2))
