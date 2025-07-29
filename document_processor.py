import PyPDF2
import docx
import requests
import tempfile
import os
from typing import List, Dict, Any
import uuid
import sqlite3
from config import Config

class DocumentProcessor:
    def __init__(self):
        Config.ensure_directories()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                url TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                content TEXT,
                page_number INTEGER,
                chunk_index INTEGER,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def download_document(self, url: str) -> str:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            suffix = '.pdf' if 'pdf' in url.lower() else '.docx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to download document: {str(e)}")
    
    def extract_pdf_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information"""
        pages = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        pages.append({
                            'page_number': page_num + 1,
                            'content': text.strip()
                        })
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")
        
        return pages
    
    def extract_docx_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append(para.text.strip())
            
            return [{
                'page_number': 1,
                'content': '\n'.join(content)
            }]
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks"""
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks
    
    async def process_document(self, url: str) -> str:
        """Process document and return document ID"""
        document_id = str(uuid.uuid4())
        
        # Download document
        file_path = await self.download_document(url)
        
        try:
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                pages = self.extract_pdf_text(file_path)
            elif file_path.endswith('.docx'):
                pages = self.extract_docx_text(file_path)
            else:
                raise Exception("Unsupported file format")
            
            # Combine all pages
            full_content = '\n\n'.join([page['content'] for page in pages])
            
            # Store document in database
            conn = sqlite3.connect(Config.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (id, url, content, metadata) VALUES (?, ?, ?, ?)",
                (document_id, url, full_content, '{}')
            )
            
            # Create and store chunks
            chunk_id_counter = 0
            for page in pages:
                chunks = self.chunk_text(page['content'])
                for chunk_index, chunk_content in enumerate(chunks):
                    chunk_id = f"{document_id}_{chunk_id_counter}"
                    cursor.execute(
                        "INSERT INTO chunks (id, document_id, content, page_number, chunk_index, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                        (chunk_id, document_id, chunk_content, page['page_number'], chunk_index, '{}')
                    )
                    chunk_id_counter += 1
            
            conn.commit()
            conn.close()
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        return document_id