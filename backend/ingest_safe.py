# ingest_safe.py
import os, glob, uuid
from pathlib import Path
import chromadb
from chromadb.config import Settings

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_store"           # <-- single, fixed location
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION = "college_docs"

def get_client():
    # Persistent on-disk DB so app + ingest see same data
    return chromadb.PersistentClient(path=str(CHROMA_DIR),
                                     settings=Settings(anonymized_telemetry=False))

def read_text_files():
    data_dirs = [BASE_DIR / "knowledge", BASE_DIR / "uploads"]
    texts = []
    for d in data_dirs:
        if d.exists():
            for p in glob.glob(str(d / "**" / "*.*"), recursive=True):
                if p.lower().endswith((".txt", ".md")):
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        texts.append((p, f.read()))
    return texts

if __name__ == "__main__":
    print("🚀 Initializing ChromaDB client...")
    os.environ["CHROMA_TELEMETRY_IMPL"] = "none"
    os.environ["CHROMA_TELEMETRY_DISABLED"] = "1"

    client = get_client()

    # Create (or get) collection
    col = client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )
    # (Optional) clear previous to keep runs deterministic
    try:
        if col.count() > 0:
            ids = col.get()["ids"]
            if ids:
                col.delete(ids=ids)
    except Exception:
        pass

    pairs = read_text_files()

    if not pairs:
        print("⚠️ No files found in 'knowledge' or 'uploads'. Ingesting a tiny placeholder so collection exists.")
        pairs = [("placeholder.txt", "This is a placeholder note for the college knowledge base.")]

    docs, metadatas, ids = [], [], []
    for path, text in pairs:
        text = text.strip()
        if not text:
            continue
        docs.append(text)
        metadatas.append({"source": path})
        ids.append(str(uuid.uuid4()))

    print(f"➕ Adding {len(docs)} chunks to '{COLLECTION}'...")
    if docs:
        col.add(documents=docs, metadatas=metadatas, ids=ids)

    print(f"✅ Ingestion complete! Count = {col.count()} docs in '{COLLECTION}'.")
    print(f"📁 Store path: {CHROMA_DIR}")