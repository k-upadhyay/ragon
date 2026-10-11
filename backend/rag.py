import io
from typing import Optional, Dict, Any, List
from pypdf import PdfReader
from qdrant_client import QdrantClient

# LangChain components
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    GEMINI_CHAT_MODEL,
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    USE_QDRANT_CLOUD,
)

# Global state tracking active document
current_document: Dict[str, Any] = {"filename": None, "chunks_count": 0}
vector_store: Optional[QdrantVectorStore] = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initialize Google Gemini Embeddings."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in backend/.env")
    return GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize Google Gemini Chat Model."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in backend/.env")
    return ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from uploaded PDF or TXT files."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages_text).strip()
    else:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1")


def index_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    1. Extracts text from file.
    2. Splits into overlapping chunks.
    3. Wipes previous collection to guarantee only the new file is queried.
    4. Embeds chunks and creates fresh Qdrant VectorStore.
    """
    global vector_store, current_document

    raw_text = extract_text(file_bytes, filename)
    if not raw_text.strip():
        raise ValueError("Could not extract any readable text from this file.")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    text_chunks = splitter.split_text(raw_text)

    docs = [
        Document(page_content=chunk, metadata={"source": filename, "chunk": idx})
        for idx, chunk in enumerate(text_chunks)
    ]

    embeddings = get_embeddings()

    # If using Qdrant Cloud, explicitly delete any previous collection to start fresh
    if USE_QDRANT_CLOUD:
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=15.0)
            client.delete_collection(QDRANT_COLLECTION_NAME)
        except Exception:
            pass

        vector_store = QdrantVectorStore.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=QDRANT_COLLECTION_NAME,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            force_recreate=True,
        )
    else:
        vector_store = QdrantVectorStore.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=QDRANT_COLLECTION_NAME,
            location=":memory:",
            force_recreate=True,
        )

    current_document = {"filename": filename, "chunks_count": len(docs)}
    return current_document


def ask_document(question: str) -> Dict[str, Any]:
    """
    1. Retrieves the most relevant chunks from the vector store.
    2. Formats them as context.
    3. Asks Gemini for a grounded answer.
    """
    global vector_store

    # Auto-reconnect to Qdrant Cloud if backend reloaded
    if not vector_store and USE_QDRANT_CLOUD:
        try:
            embeddings = get_embeddings()
            vector_store = QdrantVectorStore.from_existing_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                embedding=embeddings,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
            )
        except Exception:
            vector_store = None

    if not vector_store:
        raise ValueError("No document has been uploaded yet. Please upload a file first.")

    # Retrieve top 3 relevant chunks
    matched_docs = vector_store.similarity_search(question, k=3)

    if not matched_docs:
        return {
            "answer": "I could not find any relevant information in the uploaded document.",
            "sources": [],
            "filename": current_document["filename"],
        }

    # Build prompt
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant. Answer the user's question ONLY using the context provided below.
If the answer cannot be found in the context, say "I cannot find the answer in the uploaded document."

Context:
{context}

Question:
{question}

Answer:"""
    )

    context_str = "\n\n---\n\n".join([d.page_content for d in matched_docs])

    # Call LLM
    response = (prompt | get_llm()).invoke({"context": context_str, "question": question})

    # Robust text extraction
    if hasattr(response, "text") and response.text:
        answer_text = response.text
    elif isinstance(response.content, str):
        answer_text = response.content
    elif isinstance(response.content, list):
        answer_text = " ".join(
            [b.get("text", "") for b in response.content if isinstance(b, dict) and "text" in b]
        ) or str(response.content)
    else:
        answer_text = str(response.content)

    return {
        "answer": answer_text,
        "sources": [d.page_content for d in matched_docs],
        "filename": current_document["filename"],
    }


def reset_document() -> None:
    """Clear active document and delete vector store data."""
    global vector_store, current_document
    vector_store = None
    current_document = {"filename": None, "chunks_count": 0}

    if USE_QDRANT_CLOUD:
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10.0)
            client.delete_collection(QDRANT_COLLECTION_NAME)
        except Exception:
            pass


def get_current_status() -> Dict[str, Any]:
    """Returns the filename and chunk count of the active document."""
    return current_document
