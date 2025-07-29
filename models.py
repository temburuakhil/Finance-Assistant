from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class Source(BaseModel):
    chunk_id: str
    relevance_score: float
    document_section: str
    page_number: Optional[int] = None

class Answer(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[Source]
    reasoning: str

class QueryResponse(BaseModel):
    answers: List[str]  # Simplified for API compatibility
    processing_time: Optional[str] = None
    tokens_used: Optional[int] = None

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    page_number: Optional[int]
    chunk_index: int
    metadata: Dict[str, Any] = {}