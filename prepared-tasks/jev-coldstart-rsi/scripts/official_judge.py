#!/usr/bin/env python3
"""Fail closed: prediction-file diagnostics cannot mint an official reward."""
import json,sys
print(json.dumps({'status':'unscored','score':None,'reason':'Official trusted broker, platform isolation and image payload integration have not been activated. Use CPU diagnostics only.'}))
sys.exit(2)
