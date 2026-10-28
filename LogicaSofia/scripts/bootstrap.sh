#!/usr/bin/env bash
set -euo pipefail
if [[ "$(uname -s)" != "Linux" ]]; then
  echo 'LogicaSofia bootstrap currently targets Linux.' >&2
  exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation -e .
echo 'Installed. Use: source .venv/bin/activate && logicasofia inventory'
