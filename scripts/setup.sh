#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install -e "${ROOT_DIR}"

echo "Environment ready."
echo "Activate with: source ${VENV_DIR}/bin/activate"
echo "Run detector with: ai-detect examples/sample_ai_like.txt --json"
