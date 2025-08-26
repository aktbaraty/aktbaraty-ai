# Aktbaraty AI — Full Stack (Local RAG on PDFs, Arabic)

هذا المشروع يوفّر Backend محلي (FastAPI + llama.cpp) وواجهة Frontend ثابتة (HTML/JS) مع Nginx يقوم بعكس الطلبات لـ /ask و /search إلى الباكند.
لا توجد أي API خارجية — كل شيء يعمل محليًا.

## المتطلبات
- Docker & Docker Compose (للنشر السريع)، أو Python 3.11 لتشغيل الباكند يدويًا.
- تنزيل النماذج محليًا:
  - Embeddings (مثلاً BAAI/bge-m3) إلى `models/embeddings/`
  - LLM GGUF (مثلاً qwen2.5-7b-instruct-q4_k_m.gguf) إلى `models/llm/` وتحديث المسار في `backend/settings.py`

## تشغيل سريع باستخدام Docker
```bash
cd docker
docker compose up -d --build
# افتح المتصفح على http://localhost:8080
```
> ضع ملفات PDF في `data/pdfs/` ثم شغّل الفهرسة داخل الحاوية أو محليًا قبل طرح الأسئلة.

### فهرسة PDF داخل الحاوية
ادخل للحاوية وشغّل سكربت الفهرسة:
```bash
docker compose exec backend bash -lc "cd backend && python ingest.py"
```

## تشغيل يدوي دون Docker
1) ثبّت الاعتمادات:
```bash
cd backend
pip install -r requirements.txt
```
2) ضع ملفات PDF في `../data/pdfs/`، ثم ابنِ الفهرس:
```bash
python ingest.py
```
3) شغّل الباكند:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
4) قدّم الواجهة من أي خادم ملفات (أو افتح `frontend/index.html` مباشرة)، مع جعل `/ask` تشير إلى `http://localhost:8000/ask` إذا كنت تختبر محليًا.

## ربط نطاق فرعي (ai.aktbaraty.com)
إذا لديك Nginx خارج Docker على الخادم الرئيسي:
- اجعل الموقع الثابت تحت `/var/www/ai.aktbaraty.com` (انسخ محتوى `frontend/`).
- أضف توجيه عكسي للمسارات `/ask` و `/search` نحو `http://127.0.0.1:8000` حيث يعمل الباكند.

## بنية المجلدات
```
aktbaraty-ai/
├─ backend/          # FastAPI + RAG
├─ data/pdfs/        # ضع ملفات PDF هنا
├─ index/            # faiss.index + meta.json بعد الفهرسة
├─ models/
│  ├─ embeddings/    # مجلد نموذج Embeddings (محلي)
│  └─ llm/           # ملف GGUF للنموذج اللغوي
├─ frontend/         # موقع ثابت بسيط
└─ docker/           # Dockerfiles + nginx + compose
```

## ملاحظات
- تذكّر تحديث `backend/settings.py:LLM_PATH` باسم ملف GGUF الذي تضعه.
- إن كان لديك GPU، يمكنك تسريع llama.cpp عبر ضبط `n_gpu_layers` في `backend/main.py`.
- يدعم العربية بالكامل (retrieval + توليد).
