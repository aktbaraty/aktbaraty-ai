# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from pathlib import Path

from rag import Retriever, build_prompt_ar
from settings import LLM_PATH, TOP_K

app = FastAPI(title="Aktbaraty AI", version="1.0")


class AskReq(BaseModel):
    question: str
    top_k: int | None = None


# Lazy globals
_llm = None
_retriever = None


def get_llm():
    global _llm
    if _llm is None:
        if not Path(LLM_PATH).exists():
            raise HTTPException(status_code=500, detail=f"LLM model file not found at {LLM_PATH}. Place a GGUF file there.")
        # Adjust n_threads/n_gpu_layers to your machine
        _llm = Llama(model_path=str(LLM_PATH), n_threads=6, n_gpu_layers=0)  # set n_gpu_layers>0 if you have GPU acceleration
    return _llm


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever(top_k=TOP_K)
    return _retriever


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
def search(q: str, k: int | None = None):
    retriever = get_retriever()
    hits = retriever.search(q, top_k=k)
    return {"results": hits}


@app.post("/ask")
def ask(req: AskReq):
    retriever = get_retriever()
    hits = retriever.search(req.question, top_k=req.top_k)
    prompt = build_prompt_ar(req.question, hits)

    llm = get_llm()
    out = llm(prompt=prompt, max_tokens=512, temperature=0.2)
    answer = out["choices"][0]["text"].strip()

    return {"answer": answer, "sources": [{"source": h["source"], "chunk": h["chunk_index"], "score": h["score"]} for h in hits]}
