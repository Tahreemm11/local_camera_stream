from pathlib import Path
import chromadb
from django.conf import settings
from datetime import datetime

CHROMA_DIR = Path(settings.BASE_DIR) / "chroma_db"
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection("emotions")

def upsert_emotion(person_id: int, vector: list[float], labels: dict):
    doc_id = f"{person_id}-{datetime.utcnow().isoformat()}"
    collection.upsert(
        ids=[doc_id],
        embeddings=[vector],
        metadatas=[{"person_id": person_id, **labels}],
        documents=[str(labels)],
    )
    return doc_id

def search_emotions(query_vector: list[float], k=5, person_id: int | None = None):
    where = {"person_id": person_id} if person_id else None
    return collection.query(query_embeddings=[query_vector], n_results=k, where=where)
