import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import config
from agent.rag import build_index

config.require_api_key()
count = build_index()
print(f"Indexed {count} chunks into '{config.CHROMA_COLLECTION}' at {config.CHROMA_PERSIST_DIR}")
