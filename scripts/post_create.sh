#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r backend/requirements.txt
mkdir -p models/embeddings models/llm data/pdfs index
echo "[post_create] Done. Run: bash scripts/setup_models.sh then bash scripts/index_and_run.sh"
