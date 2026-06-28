#!/bin/bash
# gpu-run.sh -- Acquire exclusive GPU lock, pin clocks, run command, release.
#
# Usage:
#   ./gpu-run.sh python3 scripts/bench.py workspaces/fi_002_...
#
# Environment:
#   GPU_ID  -- GPU device index (default: 0)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../config.env"

LOCK_FILE="$GPU_LOCK_FILE"
GPU_ID=${GPU_ID:-0}

export FLASHINFER_TRACE_DIR=${FLASHINFER_TRACE_DIR:-$SOL_ROOT/data}

(
  flock -x 200

  # Pin clocks for reproducible benchmarks (may fail without permission — non-fatal)
  nvidia-smi -i "$GPU_ID" -lgc 1980,1980 &>/dev/null || true
  nvidia-smi -i "$GPU_ID" -lmc 2619 &>/dev/null || true

  "$@"
  EXIT_CODE=$?

  # Reset clocks
  nvidia-smi -i "$GPU_ID" -rgc &>/dev/null || true
  nvidia-smi -i "$GPU_ID" -rmc &>/dev/null || true

  exit $EXIT_CODE
) 200>"$LOCK_FILE"
