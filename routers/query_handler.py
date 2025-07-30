from fastapi import APIRouter
from services.document_parser import extract_text_from_pdf
from services.embedding_search import build_vector_store, search_similar_chunks
from utils.chunker import chunk_text
from models.schemas import QueryRequest, QueryResponse
from services.llm_local import generate_answer_with_gemini

import tempfile
import requests

router = APIRouter()

@router.post("/hackrx/run", response_model=QueryResponse)
async def run_query(query: QueryRequest):
    # Download the file from the URL
    response = requests.get(query.documents)
    if response.status_code != 200:
        return {"answers": ["Failed to download document."] * len(query.questions)}

    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        temp_path = tmp.name

    # Process document
    text = extract_text_from_pdf(temp_path)  # same function as before
    chunks = chunk_text(text)
    build_vector_store(chunks)

    # Answer each question using Gemini
    answers = []
    for q in query.questions:
        top_chunks = search_similar_chunks(q)
        context = "\n".join(top_chunks)
        answer = generate_answer_with_gemini(q, context)
        cleaned = answer.replace("*", " ").replace("\n", " ").strip()
        answers.append(cleaned)

    return {"answers": answers}
