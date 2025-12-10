# retrieval.py
from pathlib import Path
import chromadb
from chromadb.config import Settings

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_store"     # <-- same as ingest
COLLECTION = "college_docs"

class Retriever:
    def __init__(self, top_k: int = 4):
        self.top_k = top_k
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        # If not present (fresh machine), create it so app never crashes
        self.col = self.client.get_or_create_collection(
            name=COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )

    def search(self, query: str):
        if not query.strip():
            return []
        res = self.col.query(query_texts=[query], n_results=self.top_k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [{"text": d, "meta": m} for d, m in zip(docs, metas)]