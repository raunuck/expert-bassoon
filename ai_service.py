import os
import json
import random
import re
from pydantic import BaseModel
from google import genai

# Initialize the Gemini client
try:
    client = genai.Client()
except Exception:
    client = None

import qa_engine
from ai.extractive_summarizer import summarize_text
from ai.keyword_extractor import extract_keywords

def summarize_notes(notes: str, summary_type: str = "detailed") -> str:
    if not notes.strip():
        return ""
    
    if summary_type == "short":
        # Using extractive summarizer for short summaries due to pipeline incompatibility
        return summarize_text(notes, num_sentences=2)
            
    elif summary_type == "detailed":
        return summarize_text(notes, num_sentences=7)
        
    elif summary_type == "bullets":
        summary = summarize_text(notes, num_sentences=5)
        # Convert sentences to bullets
        sentences = [s.strip() for s in summary.split('.') if len(s.strip()) > 5]
        bullet_points = [f"- {s}" for s in sentences]
        return "\n".join(bullet_points)
        
    else:
        return summarize_text(notes, num_sentences=5)

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

class Quiz(BaseModel):
    questions: list[QuizQuestion]

def generate_quiz(notes: str) -> dict:
    keywords = extract_keywords(notes, top_n=15)
    
    sentences = [s.strip() + '.' for s in notes.split('.') if len(s.strip()) > 10]
    
    questions = []
    used_sentences = set()
    
    for kw in keywords:
        if len(questions) >= 5:
            break
            
        # Find a sentence containing the keyword
        for idx, sentence in enumerate(sentences):
            if idx in used_sentences:
                continue
                
            # Basic case-insensitive word boundary check
            if f" {kw.lower()} " in f" {sentence.lower()} " or sentence.lower().startswith(f"{kw.lower()} "):
                # Create a fill-in-the-blank question
                # Replace keyword (case insensitive)
                question_text = re.sub(rf'\b{re.escape(kw)}\b', '_________', sentence, flags=re.IGNORECASE)
                
                # If nothing was replaced, skip
                if question_text == sentence:
                    continue
                    
                # Generate options
                correct_option = kw
                other_options = [k for k in keywords if k != kw]
                random.shuffle(other_options)
                
                options = [correct_option] + other_options[:3]
                # Ensure we have 4 options even if we don't have enough keywords
                while len(options) < 4:
                    dummy = f"Option {len(options)+1}"
                    if dummy not in options:
                        options.append(dummy)
                        
                random.shuffle(options)
                
                questions.append({
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_option
                })
                used_sentences.add(idx)
                break
                
    # Fallback if we couldn't generate 5 questions
    while len(questions) < 5:
        idx = len(questions) + 1
        questions.append({
            "question": f"Which of the following is a key concept in the text? (Question {idx})",
            "options": ["Machine Learning", "Biology", "History", "Physics"],
            "correct_answer": "Machine Learning"
        })
        
    return {"questions": questions}

def chat_about_notes(notes: str, chat_history: list) -> str:
    if not client:
        return "Error: Google Gemini client is not initialized. Please check your GEMINI_API_KEY."

    history_text = "Conversation History:\n"
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['text']}\n"
    
    prompt = f"""You are a helpful study assistant. 
Base your answers primarily on the following notes. 
If the answer cannot be found in the notes, you can use your general knowledge, but clearly mention that it wasn't in the notes.
Use markdown formatting for your response.

Notes:
{notes}

{history_text}
Assistant:"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"I encountered an error trying to answer your question via Gemini: {str(e)}"
