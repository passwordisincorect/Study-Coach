#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export STUDY_COACH_PORT="${STUDY_COACH_PORT:-8780}"
exec python3 server.py
