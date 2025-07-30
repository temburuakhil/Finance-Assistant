import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.IndexFlatL2(384)  # 384 dims for MiniLM
chunks = []

def build_vector_store(chunk_list):
    global chunks
    chunks = chunk_list
    embeddings = model.encode(chunk_list)
    index.add(np.array(embeddings))

def search_similar_chunks(query, top_k=3):
    query_vector = model.encode([query])
    D, I = index.search(np.array(query_vector), top_k)
    return [chunks[i] for i in I[0]]
