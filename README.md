# AI Study Assistant

AI Study Assistant is a comprehensive web application designed to help students and learners process, understand, and retain information from their study notes. The application leverages Google's Gemini AI to provide advanced summarization, quiz generation, and interactive chat functionalities based on your notes.

## Features

- **📝 AI-Powered Summarization**: Summarize your study notes in multiple styles including short, detailed, and bulleted lists.
- **❓ Automatic Quiz Generation**: Instantly generate multiple-choice quizzes from your notes to test your knowledge.
- **📄 PDF Note Extraction**: Upload PDF documents to automatically extract text and use it as your study notes.
- **💬 Interactive Chat Interface**: Ask questions and chat contextually with an AI assistant based directly on the contents of your study notes.

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI Integration**: Google Gemini (`gemini-2.5-flash`) using `google-genai` SDK
- **PDF Processing**: `pypdf`
- **Data Validation**: Pydantic
- **Frontend**: HTML/CSS/JS (served as static files)


## Project Structure

```
Antigravity/
│
├── main.py                   # FastAPI application entry point and routing
├── ai_service.py             # Functions to interact with Google Gemini AI
├── qa_engine.py              # Question-answering engine integration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables configuration
│
├── static/                   # Frontend assets (HTML, CSS, JS)
│
└── ai/                       # Local AI/ML capabilities
    ├── train_models.py
    ├── extractive_summarizer.py
    ├── keyword_extractor.py
    ├── model.pkl
    └── data.pkl
```

## Setup & Installation

1. **Clone or Navigate to the Project Directory**
   Ensure you are in the project root folder.

2. **Create a Virtual Environment (Optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Install the required Python packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Make sure you have a `.env` file in the root directory. You need to provide your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or you can run the `main.py` directly:
```bash
python main.py
```


The application will be accessible at:
- Application UI: `http://localhost:8000/`
- API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

- `POST /api/summarize`: Expects `{ "notes": "...", "summary_type": "short|detailed|bullets" }`. Returns a summary.
- `POST /api/generate-quiz`: Expects `{ "notes": "..." }`. Returns a 5-question multiple choice quiz in JSON format.
- `POST /api/upload-pdf`: Expects a multipart form data with a `file` field containing a PDF. Returns the extracted text.
- `POST /api/chat`: Expects `{ "notes": "...", "chat_history": [{"role": "user", "text": "..."}] }`. Returns an AI response based on the notes and chat history.
