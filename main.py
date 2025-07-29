from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import asyncio
from typing import List
import logging

from models import QueryRequest, QueryResponse
from document_processor import DocumentProcessor
from retrieval_engine import RetrievalEngine
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for processors
document_processor = None
retrieval_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global document_processor, retrieval_engine
    
    # Startup
    Config.ensure_directories()
    document_processor = DocumentProcessor()
    retrieval_engine = RetrievalEngine()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="Process documents and answer queries using semantic search and LLM",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Expected token (in production, use environment variables)
EXPECTED_TOKEN = "ec50966dd6ad633d5d916660e0ce299987cc4be90656b981fb49b9ffa8042e1c"

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials

@app.get("/")
async def root():
    return {"message": "LLM Query-Retrieval System is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """
    Main endpoint to process documents and answer questions
    """
    global document_processor, retrieval_engine
    start_time = time.time()
    
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Process document
        logger.info("Processing document...")
        document_id = await document_processor.process_document(request.documents)
        
        # Add embeddings for the document
        logger.info("Generating embeddings...")
        retrieval_engine.embedding_engine.add_document_embeddings(document_id)
        
        # Process each question
        answers = []
        total_tokens = 0
        
        for question in request.questions:
            logger.info(f"Processing question: {question[:50]}...")
            
            result = retrieval_engine.process_query(document_id, question)
            answers.append(result['answer'])
            
            # Estimate tokens (rough approximation)
            total_tokens += len(question.split()) + len(result['answer'].split())
        
        processing_time = f"{time.time() - start_time:.2f}s"
        
        logger.info(f"Request completed in {processing_time}")
        
        return QueryResponse(
            answers=answers,
            processing_time=processing_time,
            tokens_used=total_tokens
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/v1/documents/process")
async def process_document_only(
    document_url: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """
    Endpoint to process and index a document without queries
    """
    global document_processor, retrieval_engine
    try:
        document_id = await document_processor.process_document(document_url)
        retrieval_engine.embedding_engine.add_document_embeddings(document_id)
        
        return {
            "document_id": document_id,
            "status": "processed",
            "message": "Document processed and indexed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/v1/documents/{document_id}/search")
async def search_document(
    document_id: str,
    query: str,
    top_k: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """
    Search within a specific document
    """
    global retrieval_engine
    try:
        result = retrieval_engine.process_query(document_id, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
