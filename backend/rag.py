cat > backend/rag.py <<'PY'
import json
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from fastembed import TextEmbedding

from settings import INDEX_PATH, META_PATH, EMB_MODEL_DIR, TOP_K


class Retriever:
    def __init__(self, top_k: int = TOP_K):
        if not INDEX_PATH.exists() or not META_PATH.exists():
            raise FileNotFoundError(
                f"Index or meta not found. Run ingest.py first.\nINDEX_PATH={INDEX_PATH}\nMETA_PATH={META_PATH}"
            )

        # اقرأ الفهرس والميتا
        self.index = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        # fastembed (خفيف ولا يتطلب Torch)
        self.embedder = TextEmbedding(
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            cache_dir=str(EMB_MODEL_DIR)
        )
        self.top_k = top_k

    def search(self, query: str, top_k: int | None = None) -> List[Dict]:
        k = top_k or self.top_k
        # fastembed يرجّع مولد؛ نحوّله إلى numpy
        q = np.array(list(self.embedder.embed([query])), dtype=np.float32)
        # L2 normalize → cosine via inner product
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        scores, idxs = self.index.search(q, k)

        hits = []
        for score, idx in zip(scores[0], idxs[0]):
            m = self.meta[int(idx)]
            hits.append({
                "score": float(score),
                "source": m["source"],
                "chunk_index": m["chunk_index"],
                "text": m["text"]
            })
        return hits


def build_prompt_ar(question: str, docs: List[Dict]) -> str:
    context = "\n\n".join(
        f"[المصدر: {d['source']} — مقطع {d['chunk_index']}]\n{d['text']}"
        for d in docs
    )
    prompt = f"""أنت مساعد خبير يجيب بالعربية الفصحى باختصار ووضوح اعتمادًا على المقتطفات التالية من وثائق PDF.
لا تخترع معلومات. إذا لم تجد الإجابة في المقتطفات، قل: لا أملك معلومات كافية من الملفات.
أظهر المصادر المستخدمة في نهاية الإجابة.

السؤال: {question}

المقتطفات:
{context}

الإجابة بالعربية:
"""
    return prompt
PY
