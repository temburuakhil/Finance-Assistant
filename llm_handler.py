from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict
import re

class LLMHandler:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad",
            device=self.device
        )
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        
    def extract_answer_from_context(self, question: str, context: str) -> Dict[str, any]:
        """Extract answer from context using QA model"""
        try:
            # Truncate context if too long
            max_length = 512
            if len(context.split()) > max_length:
                context = ' '.join(context.split()[:max_length])
            
            result = self.qa_pipeline(question=question, context=context)
            
            return {
                'answer': result['answer'],
                'confidence': result['score'],
                'reasoning': f"Found answer in context with {result['score']:.2f} confidence"
            }
        except Exception as e:
            return {
                'answer': "Unable to extract specific answer from the provided context.",
                'confidence': 0.1,
                'reasoning': f"Error in processing: {str(e)}"
            }
    
    def generate_comprehensive_answer(self, question: str, contexts: List[str]) -> Dict[str, any]:
        """Generate comprehensive answer from multiple contexts"""
        # Combine contexts
        combined_context = '\n\n'.join(contexts[:3])  # Use top 3 contexts
        
        # Extract answer using QA model
        result = self.extract_answer_from_context(question, combined_context)
        
        # Enhance the answer if confidence is low
        if result['confidence'] < 0.3:
            # Try to find relevant sentences
            relevant_sentences = []
            question_words = set(question.lower().split())
            
            for context in contexts:
                sentences = re.split(r'[.!?]+', context)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 20:
                        sentence_words = set(sentence.lower().split())
                        overlap = len(question_words.intersection(sentence_words))
                        if overlap >= 2:
                            relevant_sentences.append(sentence)
            
            if relevant_sentences:
                result['answer'] = '. '.join(relevant_sentences[:2])
                result['confidence'] = min(0.7, result['confidence'] + 0.3)
                result['reasoning'] = "Answer compiled from relevant document sections"
        
        return result