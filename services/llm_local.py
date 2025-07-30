import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_answer_with_gemini(question: str, context: str) -> str:
    prompt = f"""
You are an expert in insurance and legal documents.
Using the following policy context, answer the user's question clearly.

Context:
{context}

Question:
{question}

Answer:
"""
    response = model.generate_content(prompt)
    import re

    def clean_output(text):
        text = re.sub(r'[\*\n]+', ' ', text)   # remove * and newlines
        text = re.sub(r'\s+', ' ', text)       # collapse multiple spaces
        return text.strip()

    return clean_output(response.text)

