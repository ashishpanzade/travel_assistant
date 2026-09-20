"""Central configuration loaded from environment variables / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

_persist_dir = Path(os.getenv("CHROMA_PERSIST_DIR", "./vectorstore"))
CHROMA_PERSIST_DIR = str(_persist_dir if _persist_dir.is_absolute() else BASE_DIR / _persist_dir)
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "singapore_travel")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
MCP_SERVERS_DIR = BASE_DIR / "mcp_servers"


def require_api_key() -> None:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your "
            "Google AI Studio API key (https://aistudio.google.com/apikey)."
        )
