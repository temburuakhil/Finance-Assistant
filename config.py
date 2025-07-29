import os
from typing import Optional

class Config:
    # API Configuration
    API_VERSION = "v1"
    BASE_URL = "http://localhost:8000"
    
    # Model Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL = "microsoft/DialoGPT-medium"  # Free alternative
    
    # Vector Database
    FAISS_INDEX_PATH = "data/faiss_index"
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5
    
    # Database
    DATABASE_PATH = "data/documents.db"
    
    # Directories
    DATA_DIR = "data"
    TEMP_DIR = "temp"
    
    @classmethod
    def ensure_directories(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)