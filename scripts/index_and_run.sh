#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate

if [ ! -d models/embeddings ] || [ ! -d models/llm ]; then
  echo "[ERR] Missing models. Run: bash scripts/setup_models.sh"
  exit 1
fi

pushd backend >/dev/null
python ingest.py
uvicorn main:app --host 0.0.0.0 --port 8000
popd >/dev/null
