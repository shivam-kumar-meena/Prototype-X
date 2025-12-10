import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import chromadb
from chromadb.config import Settings

# ============ CONFIG ============
COLLECTION = "college_docs"
PERSIST_DIR = "chroma_store"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # you can replace "*" with your Netlify URL later

# ============ INITIALIZE CHROMADB ============
os.environ["ANONYMIZED_TELEMETRY"] = "false"

client = chromadb.Client(Settings(
    is_persistent=True,
    persist_directory=PERSIST_DIR,
))

try:
    collection = client.get_collection(COLLECTION)
except Exception:
    collection = client.create_collection(COLLECTION)


# ============ HELPERS ============
def retrieve_context(query: str, k: int = 3):
    """Fetch most relevant stored chunks from ChromaDB."""
    try:
        res = collection.query(query_texts=[query], n_results=k)
        docs = res.get("documents", [[]])[0]
        sources = res.get("metadatas", [[]])[0]
        pairs = []
        for d, m in zip(docs, sources):
            src = m.get("source") if isinstance(m, dict) else ""
            pairs.append((src, d))
        return pairs
    except Exception:
        return []


def build_system_prompt(tone="Professional", lang="Auto", prefer_hinglish=True):
    """System instruction for Groq model."""
    tone_map = {
        "Casual": "Friendly and relaxed tone",
        "Professional": "Professional and informative tone",
        "Coach": "Supportive and motivational tone"
    }
    base = f"You are Prototype-X, a helpful and concise assistant. Tone: {tone_map.get(tone,'Professional')}."

    if lang == "Auto":
        if prefer_hinglish:
            base += " If user mixes Hindi and English, reply naturally in Hinglish."
        else:
            base += " Detect and use the user's language automatically."
    elif lang == "Hindi":
        base += " Reply in Hindi."
    elif lang == "English":
        base += " Reply in professional English."
    elif lang == "Hinglish":
        base += " Reply in clean Hinglish."

    base += " Keep answers short, accurate, and friendly. Do not invent facts."
    return base


def build_user_prompt(user_text: str, memory_data: str, context_pairs):
    """Construct user query with memory and retrieved context."""
    ctx = ""
    if context_pairs:
        joined = "\n\n".join([f"[{src}] {text}" for src, text in context_pairs if text])
        ctx = f"\n\nRelevant college context:\n{joined}"
    mem = ""
    if memory_data:
        mem = f"\n\nUser Memory:\n{memory_data}"
    return f"User: {user_text}{mem}{ctx}\n\nRespond helpfully."


def groq_chat(system_prompt, user_prompt):
    """Send query to Groq model."""
    if not GROQ_API_KEY:
        return "(⚠️ Missing GROQ_API_KEY in environment.)"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.6,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(Groq error: {e})"


# ============ API ROUTES ============
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Prototype-X backend is running"})


@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint."""
    data = request.get_json()
    user_text = data.get("message", "")
    memory = data.get("memory", "")
    tone = data.get("tone", "Professional")
    lang = data.get("lang", "Auto")
    prefer_hinglish = data.get("prefer_hinglish", True)

    context_pairs = retrieve_context(user_text)
    system_prompt = build_system_prompt(tone, lang, prefer_hinglish)
    user_prompt = build_user_prompt(user_text, memory, context_pairs)

    reply = groq_chat(system_prompt, user_prompt)

    return jsonify({"reply": reply})


@app.route("/reset_memory", methods=["POST"])
def reset_memory():
    """Clear memory (frontend-managed)."""
    return jsonify({"status": "Memory cleared"})


@app.route("/memory", methods=["GET"])
def get_memory():
    """Just return placeholder memory for now."""
    return jsonify({"memory": "Sample memory placeholder"})


# ============ DEPLOYMENT ENTRY ============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)