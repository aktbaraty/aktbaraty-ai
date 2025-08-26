# Backend — Aktbaraty AI

Minimal FastAPI backend to index local PDFs and answer Arabic queries using local LLM (no external APIs).

## Structure
- `ingest.py` — builds FAISS index from PDFs in `../data/pdfs` using a local Sentence-Transformers model.
- `rag.py` — retrieval + Arabic prompt builder.
- `main.py` — FastAPI app exposing `/search` and `/ask`.
- `settings.py` — paths and constants.
- `requirements.txt` — Python dependencies.

## Quickstart
1) Put your embedding model folder under `../models/embeddings/` (e.g., BAAI/bge-m3) and a GGUF LLM file under `../models/llm/` (update `settings.py:LLM_PATH`).
2) Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3) Index PDFs (place PDFs in `../data/pdfs/`):
   ```bash
   python ingest.py
   ```
4) Run server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5) Test:
   - Retrieval only: `GET /search?q=سؤالك`
   - RAG answer: `POST /ask` with JSON `{ "question": "..." }`
