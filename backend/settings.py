from pathlib import Path

# Project root (one level up from this file's folder)
ROOT = Path(__file__).resolve().parents[1]

# Data & index paths
DATA_DIR = ROOT / "data" / "pdfs"
INDEX_DIR = ROOT / "index"
INDEX_PATH = INDEX_DIR / "faiss.index"
META_PATH = INDEX_DIR / "meta.json"

# Models
EMB_MODEL_DIR = ROOT / "models" / "embeddings"   # Put the Sentence-Transformers model here (downloaded locally)
LLM_PATH = ROOT / "models" / "llm" / "qwen2.5-7b-instruct-q4_k_m.gguf"  # Replace with your local GGUF file name

# Chunking & retrieval
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 5
