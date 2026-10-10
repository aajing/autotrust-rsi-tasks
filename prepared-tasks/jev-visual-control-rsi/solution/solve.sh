#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$ROOT/scripts/materialize_baseline.py" --output "${1:?Provide an empty candidate output directory}"
