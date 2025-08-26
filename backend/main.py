# فعّل البيئة
source .venv/bin/activate

# ثبّت ctransformers (بديل خفيف يدعم GGUF)
pip install --no-cache-dir ctransformers==0.2.27

# انسخ ملف main.py الجديد (يستعمل ctransformers ويحدّد النوع تلقائيًا من اسم الملف)
cat > backend/main.py <<'PY'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

from rag import Retriever, build_prompt_ar
from settings import LLM_PATH, TOP_K

from ctransformers import AutoModelForCausalLM

app = FastAPI(title="Aktbaraty AI", version="1.0")

class AskReq(BaseModel):
    question: str
    top_k: Optional[int] = None

_llm = None
_retriever = None

def _infer_model_type_from_filename(path: Path) -> str:
    name = path.name.lower()
    if "qwen" in name:
        return "qwen2"
    if "llama" in name or "tinyllama" in name:
        return "llama"
    return "llama"

def get_llm():
    global _llm
    if _llm is None:
        if not Path(LLM_PATH).exists():
            raise HTTPException(status_code=500, detail=f"LLM model file not found at {LLM_PATH}.")
        model_type = _infer_model_type_from_filename(Path(LLM_PATH))
        _llm = AutoModelForCausalLM.from_pretrained(
            model_path=str(Path(LLM_PATH).parent),
            model_file=Path(LLM_PATH).name,
            model_type=model_type,
            config={"temperature": 0.2, "max_new_tokens": 512}
        )
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
def search(q: str, k: Optional[int] = None):
    retriever = get_retriever()
    hits = retriever.search(q, top_k=k)
    return {"results": hits}

@app.post("/ask")
def ask(req: AskReq):
    retriever = get_retriever()
    hits = retriever.search(req.question, top_k=req.top_k)
    prompt = build_prompt_ar(req.question, hits)

    llm = get_llm()
    answer = llm(prompt).strip()
    return {
        "answer": answer,
        "sources": [{"source": h["source"], "chunk": h["chunk_index"], "score": h["score"]} for h in hits]
    }
PY
