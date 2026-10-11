import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env specifically from backend/.env or root
backend_env = Path(__file__).resolve().parent / ".env"
root_env = Path(__file__).resolve().parent.parent / ".env"

if backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

# Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Gemini Models
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite").strip()

# Qdrant Vector DB Settings
QDRANT_URL = os.getenv("QDRANT_URL", "").strip()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip()
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "simple_rag").strip()

# Detect whether Qdrant Cloud has valid configuration
USE_QDRANT_CLOUD = bool(
    QDRANT_URL 
    and "your-cluster-url" not in QDRANT_URL 
    and QDRANT_API_KEY 
    and "your_qdrant_api_key" not in QDRANT_API_KEY
)
