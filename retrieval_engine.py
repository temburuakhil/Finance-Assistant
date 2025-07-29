import sqlite3
from typing import List, Dict, Tuple
from embedding_engine import EmbeddingEngine
from llm_handler import LLMHandler
from config import Config
import uuid

class RetrievalEngine:
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.llm_handler = LLMHandler()
    
    def get_chunk_details(self, chunk_ids: List[str]) -> List[Dict]:
        """Get detailed information about chunks"""
        if not chunk_ids:
            return []
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in chunk_ids])
        cursor.execute(f"""
            SELECT id, content, page_number, chunk_index, document_id
            FROM chunks 
            WHERE id IN ({placeholders})
        """, chunk_ids)
        
        results = cursor.fetchall()
        conn.close()
        
        chunk_details = []
        for result in results:
            chunk_details.append({
                'id': result[0],
                'content': result[1],
                'page_number': result[2],
                'chunk_index': result[3],
                'document_id': result[4]
            })
        
        return chunk_details
    
    def process_query(self, document_id: str, question: str) -> Dict:
        """Process a single query against a document"""
        # Search for similar chunks
        similar_chunks = self.embedding_engine.search_similar(
            question, 
            top_k=Config.TOP_K_RESULTS
        )
        
        if not similar_chunks:
            return {
                'answer': "No relevant information found in the document.",
                'confidence': 0.0,
                'sources': [],
                'reasoning': "No matching content found"
            }
        
        # Get chunk details
        chunk_ids = [chunk[0] for chunk in similar_chunks]
        chunk_details = self.get_chunk_details(chunk_ids)
        
        # Prepare contexts for LLM
        contexts = []
        sources = []
        
        for i, (chunk_id, score) in enumerate(similar_chunks):
            chunk_detail = next((c for c in chunk_details if c['id'] == chunk_id), None)
            if chunk_detail:
                contexts.append(chunk_detail['content'])
                sources.append({
                    'chunk_id': chunk_id,
                    'relevance_score': score,
                    'document_section': f"Page {chunk_detail['page_number']}, Section {chunk_detail['chunk_index']}",
                    'page_number': chunk_detail['page_number']
                })
        
        # Generate answer using LLM
        llm_result = self.llm_handler.generate_comprehensive_answer(question, contexts)
        
        return {
            'answer': llm_result['answer'],
            'confidence': llm_result['confidence'],
            'sources': sources,
            'reasoning': llm_result['reasoning']
        }
