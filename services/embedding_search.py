import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Lazy loading - only load when needed
_model = None
_index = None
_chunks = []

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_index():
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(384)
    return _index

def build_vector_store(chunk_list):
    global _chunks
    _chunks = chunk_list
    model = get_model()
    index = get_index()
    embeddings = model.encode(chunk_list)
    index.add(np.array(embeddings))

def search_similar_chunks(query, top_k=3):
    model = get_model()
    index = get_index()
    query_vector = model.encode([query])
    D, I = index.search(np.array(query_vector), top_k)
    return [_chunks[i] for i in I[0]]