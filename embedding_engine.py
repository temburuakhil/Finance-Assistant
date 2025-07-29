from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sqlite3
import pickle
import os
from typing import List, Tuple
from config import Config

class EmbeddingEngine:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.index = None
        self.chunk_ids = []
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        index_file = f"{Config.FAISS_INDEX_PATH}.index"
        metadata_file = f"{Config.FAISS_INDEX_PATH}.metadata"
        
        if os.path.exists(index_file) and os.path.exists(metadata_file):
            # Load existing index
            self.index = faiss.read_index(index_file)
            with open(metadata_file, 'rb') as f:
                self.chunk_ids = pickle.load(f)
        else:
            # Create new index
            self.index = faiss.IndexFlatIP(384)  # Dimension for all-MiniLM-L6-v2
            self.chunk_ids = []
    
    def save_index(self):
        """Save FAISS index and metadata"""
        os.makedirs(os.path.dirname(Config.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, f"{Config.FAISS_INDEX_PATH}.index")
        with open(f"{Config.FAISS_INDEX_PATH}.metadata", 'wb') as f:
            pickle.dump(self.chunk_ids, f)
    
    def add_document_embeddings(self, document_id: str):
        """Add embeddings for all chunks of a document"""
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, content FROM chunks WHERE document_id = ?",
            (document_id,)
        )
        chunks = cursor.fetchall()
        conn.close()
        
        if not chunks:
            return
        
        # Generate embeddings
        texts = [chunk[1] for chunk in chunks]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Update chunk IDs
        for chunk in chunks:
            self.chunk_ids.append(chunk[0])
        
        # Save updated index
        self.save_index()
    
    def search_similar(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """Search for similar chunks"""
        top_k = top_k or Config.TOP_K_RESULTS
        
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunk_ids):
                results.append((self.chunk_ids[idx], float(score)))
        
        return results