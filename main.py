from fastapi import FastAPI, HTTPException, UploadFile, File
from pypdf import PdfReader
import io
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

import ai_service

app = FastAPI(title="AI Study Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NotesRequest(BaseModel):
    notes: str
    summary_type: str = "detailed"

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    notes: str
    chat_history: list[ChatMessage]

@app.post("/api/summarize")
def summarize(req: NotesRequest):
    if not req.notes.strip():
        raise HTTPException(status_code=400, detail="Notes cannot be empty.")
    try:
        summary = ai_service.summarize_notes(req.notes, req.summary_type)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-quiz")
def generate_quiz(req: NotesRequest):
    if not req.notes.strip():
        raise HTTPException(status_code=400, detail="Notes cannot be empty.")
    try:
        quiz = ai_service.generate_quiz(req.notes)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    try:
        content = await file.read()
        pdf = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.notes.strip():
        raise HTTPException(status_code=400, detail="Notes cannot be empty.")
    if not req.chat_history:
        raise HTTPException(status_code=400, detail="Chat history cannot be empty.")
    try:
        # Convert Pydantic models to dicts
        history_dicts = [{"role": msg.role, "text": msg.text} for msg in req.chat_history]
        reply = ai_service.chat_about_notes(req.notes, history_dicts)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (HTML, CSS, JS)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
