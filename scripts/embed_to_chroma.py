# scripts/embed_to_chroma.py
import json, os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

CHUNKS_PATH = "data/chunks.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "incidents"
PERSIST_DIR = ".chroma"   # leave as ".chroma" (or change if you want a fresh dir)

def load_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def main():
    os.makedirs(PERSIST_DIR, exist_ok=True)
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print("Loading embedding model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    docs, ids, metadatas, embeddings = [], [], [], []
    count = 0
    for chunk in load_chunks(CHUNKS_PATH):
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]
        meta = {"incident_id": chunk.get("incident_id"), "service": chunk.get("service"), "chunk_index": chunk.get("chunk_index")}
        emb = model.encode([text])[0]
        docs.append(text); ids.append(chunk_id); metadatas.append(meta); embeddings.append(emb.tolist())
        count += 1
        if len(docs) >= 256:
            collection.add(documents=docs, ids=ids, metadatas=metadatas, embeddings=embeddings)
            docs, ids, metadatas, embeddings = [], [], [], []
    if docs:
        collection.add(documents=docs, ids=ids, metadatas=metadatas, embeddings=embeddings)
    print(f"Added {count} chunks to Chroma collection '{COLLECTION_NAME}' (persisted at {PERSIST_DIR})")

if __name__ == "__main__":
    main()
