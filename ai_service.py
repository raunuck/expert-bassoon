import os
import json
from pydantic import BaseModel
from google import genai

# Initialize the Gemini client
try:
    client = genai.Client()
except Exception:
    client = None

def summarize_notes(notes: str, summary_type: str = "detailed") -> str:
    if not client:
        return "Error: Google Gemini client is not initialized. Please check your GEMINI_API_KEY."

    type_prompts = {
        "short": "Provide a very brief, concise summary of the key points.",
        "detailed": "Provide a highly detailed summary with comprehensive explanations.",
        "bullets": "Provide a summary strictly formatted as a bulleted list of key takeaways."
    }
    
    instruction = type_prompts.get(summary_type, type_prompts["detailed"])
    
    prompt = f"{instruction} Use markdown formatting.\n\nNotes:\n{notes}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error during summarization: {str(e)}"

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

class Quiz(BaseModel):
    questions: list[QuizQuestion]

def generate_quiz(notes: str) -> dict:
    if not client:
        raise Exception("Google Gemini client is not initialized. Please check your GEMINI_API_KEY.")

    prompt = f"Generate a 5-question multiple choice quiz based on the following study notes. Make sure the questions test key concepts.\n\nNotes:\n{notes}"
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': Quiz,
        },
    )
    return json.loads(response.text)

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
