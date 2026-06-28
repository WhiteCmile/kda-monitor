#!/usr/bin/env bash
# init-workspace.sh -- Thin wrapper around init_workspace.py
#
# Usage:
#   ./init-workspace.sh --all              # Init all 60 workspaces
#   ./init-workspace.sh FI-002             # Init a single workspace
#   ./init-workspace.sh --group L1         # Init all L1 tasks
#   ./init-workspace.sh --list             # List tasks
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/init_workspace.py" "$@"
