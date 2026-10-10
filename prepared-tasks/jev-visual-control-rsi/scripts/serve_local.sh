#!/usr/bin/env bash
# OPERATOR ONLY. This starts GPU inference; CPU preparation never calls it.
set -euo pipefail
JEV_PATH=${1:?JEV-9B pinned snapshot directory}
BASE_PATH=${2:?Qwen3.5-9B pinned snapshot directory}
export JEV_DECIDE_SYSTEM2=0
export JEV_DECIDE_CALIBRATION="$JEV_PATH/vl/calibration.json"
exec python3 "$JEV_PATH/vl/serve_decide.py" --model "$BASE_PATH" --served-model-name autotrust/JEV-9B \
  --enable-lora --max-lora-rank 32 --lora-modules "jev-decision=$JEV_PATH/vl/adapter_vllm" \
  --logprobs-mode processed_logprobs --max-model-len 4096 --enable-prefix-caching --mamba-cache-mode align \
  --limit-mm-per-prompt '{"image": 4}' --max-num-seqs 8 --max-logprobs 256 --trust-request-chat-template \
  --host 127.0.0.1 --port 8000
