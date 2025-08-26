# backend/rag.py
import json
from pathlib import Path
import numpy as np
import faiss
from FlagEmbedding import BGEM3FlagModel

from settings import INDEX_PATH, META_PATH, EMB_MODEL_DIR, TOP_K

class Retriever:
    def __init__(self, top_k: int = TOP_K):
        if not INDEX_PATH.exists() or not META_PATH.exists():
            raise FileNotFoundError("Index or meta file not found. Run ingest.py first.")
        self.model = BGEM3FlagModel(str(EMB_MODEL_DIR), use_fp16=True)
        self.index = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        self.top_k = top_k

    def search(self, query: str, top_k: int | None = None):
        k = top_k or self.top_k
        out = self.model.encode([query], batch_size=1, max_length=8192)
        q = out['dense_vecs']
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        q = np.array(q, dtype=np.float32)
        scores, idxs = self.index.search(q, k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            m = self.meta[int(idx)]
            results.append({"score": float(score), **m})
        return results

def build_prompt_ar(question: str, docs):
    context = "\n\n".join([f"[المصدر: {d['source']} — مقطع {d['chunk_index']}]\n{d['text']}" for d in docs])
    prompt = f"""أنت مساعد خبير يجيب بالعربية الفصحى باختصار ووضوح اعتمادًا على المقتطفات التالية من وثائق PDF.
لا تخترع معلومات. إذا لم تجد الإجابة في المقتطفات، قل: لا أملك معلومات كافية من الملفات.
أظهر المصادر المستخدمة في نهاية الإجابة.

السؤال: {question}

المقتطفات:
{context}

الإجابة بالعربية:
"""
    return prompt
