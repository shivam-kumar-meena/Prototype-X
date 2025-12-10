
# Prototype-X — Integrated (Frontend + Backend)

This is a READY-TO-RUN rebuild that connects your new **Prototype-X** frontend to a Flask backend.
It reuses your old **Retriever / Memory** modules from Prototype-S when available.

## 1) Run the backend
```bash
cd backend
pip install -r requirements.txt
# optional: export GROQ_API_KEY=your_key  (for real LLM)
python app.py
```
Backend runs at: http://127.0.0.1:5000

## 2) Run the frontend
Open `frontend/index.html` with VS Code Live Server (or any static server).
```bash
# Example (Python)
cd frontend
python -m http.server 5500
# open http://127.0.0.1:5500/index.html
```

## 3) Use it
- Type a message and hit ➤
- The frontend calls `POST /chat` with your controls (mode, model, Hinglish, etc.)
- Backend retrieves top docs (if vectordb present), builds a prompt, and replies.
- If `GROQ_API_KEY` is set, it uses Groq LLM. Otherwise, it returns a safe offline demo text.

## Notes
- The backend attempts to use your existing `retrieval.py` and `memory_store.py` (copied in `backend/`).  
- If your `vectordb/` was created elsewhere, move it next to `backend/` or reindex as per your old ingestion script.
