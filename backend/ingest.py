# backend/ingest.py
import json, uuid
from pathlib import Path
import fitz  # PyMuPDF
from FlagEmbedding import BGEM3FlagModel
import faiss
import numpy as np

from settings import DATA_DIR, INDEX_DIR, META_PATH, INDEX_PATH, EMB_MODEL_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def load_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        text = page.get_text("text") or ""
        if text.strip():
            texts.append(text)
    return "\n".join(texts)

def chunk_text(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    n = len(text)
    step = max(1, size - overlap)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks

def main():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    model = BGEM3FlagModel(str(EMB_MODEL_DIR), use_fp16=True)
    dim = 1024  # BGE-M3 dense vector dimension
    index = faiss.IndexFlatIP(dim)

    meta = []
    all_vecs = []

    pdfs = sorted(DATA_DIR.glob("**/*.pdf"))
    if not pdfs:
        print("[!] No PDFs found in", DATA_DIR)
        return

    total_chunks = 0
    for pdf in pdfs:
        print(f"[+] Reading {pdf}")
        full_text = load_text_from_pdf(pdf)
        if not full_text.strip():
            print("    [!] Empty/No text extracted, skipping.")
            continue
        chunks = chunk_text(full_text)
        if not chunks:
            print("    [!] No chunks created, skipping.")
            continue

        out = model.encode(chunks, batch_size=32, max_length=8192)
        emb = out['dense_vecs']
        # L2 normalize for cosine similarity with Inner Product index
        emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
        all_vecs.append(emb)
        for i, ch in enumerate(chunks):
            meta.append({
                "id": str(uuid.uuid4()),
                "source": str(pdf.relative_to(DATA_DIR)),
                "chunk_index": i,
                "text": ch
            })
        total_chunks += len(chunks)

    if not meta:
        print("[!] No metadata/chunks built. Aborting.")
        return

    mat = np.vstack(all_vecs).astype("float32")
    index.add(mat)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    faiss.write_index(index, str(INDEX_PATH))
    print(f"[✓] Index saved: {INDEX_PATH}")
    print(f"[✓] Meta saved:  {META_PATH}")
    print(f"[✓] Total chunks: {total_chunks}")

if __name__ == "__main__":
    main()
