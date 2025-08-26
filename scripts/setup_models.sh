#!/usr/bin/env bash
set -euo pipefail
EMB_REPO="${EMB_REPO:-https://huggingface.co/BAAI/bge-m3}"
LLM_FILE="${LLM_FILE:-Qwen2.5-7B-Instruct-Q4_K_M.gguf}"
LLM_REPO="${LLM_REPO:-https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF}"

echo "[models] Embeddings → models/embeddings/bge-m3"
mkdir -p models/embeddings
if [ ! -d "models/embeddings/bge-m3" ]; then
  git lfs install
  git clone "$EMB_REPO" models/embeddings/bge-m3
fi

echo "[models] LLM → models/llm/${LLM_FILE}"
mkdir -p models/llm
if [ ! -f "models/llm/${LLM_FILE}" ]; then
  wget -O "models/llm/${LLM_FILE}"     "${LLM_REPO}/resolve/main/${LLM_FILE}?download=true"
fi

echo "[models] Tip: For a tiny smoke test, set:"
echo "  export LLM_REPO=https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
echo "  export LLM_FILE=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
