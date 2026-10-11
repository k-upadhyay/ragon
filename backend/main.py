from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag import index_document, ask_document, get_current_status, reset_document

# Initialize FastAPI application
app = FastAPI(title="Simple RAG API", version="1.0.0")

# Enable CORS so Next.js frontend can communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    """Check if the backend is running and get currently loaded document."""
    status = get_current_status()
    return {"status": "ok", "uploaded_file": status["filename"]}


@app.get("/status")
def status_check():
    """Get active document info."""
    return get_current_status()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload ONE document (PDF or TXT), chunk it, and index it into vector DB."""
    try:
        content_bytes = await file.read()
        filename = file.filename or "uploaded_file"
        result = index_document(content_bytes, filename)
        return {
            "message": f"Successfully indexed {result['filename']}!",
            "filename": result["filename"],
            "chunks": result["chunks_count"],
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.post("/ask")
def ask(payload: AskRequest):
    """Ask a question about the uploaded document."""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return ask_document(payload.question.strip())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@app.post("/reset")
def reset():
    """Reset the current document and delete its vectors."""
    reset_document()
    return {"message": "Document reset successfully."}
