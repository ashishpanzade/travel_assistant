import time

import frontmatter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from . import config

_store = None


def get_vectorstore():
    global _store
    if _store is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL, google_api_key=config.GOOGLE_API_KEY
        )
        _store = Chroma(
            collection_name=config.CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
        )
    return _store


def load_chunks():
    by_header = MarkdownHeaderTextSplitter(
        [("#", "h1"), ("##", "h2"), ("###", "h3")], strip_headers=False
    )
    by_size = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    chunks = []
    for path in sorted(config.RAW_DATA_DIR.glob("*.md")):
        page = frontmatter.load(path)
        source = {"title": page.get("title", path.stem), "source_url": page.get("source_url", "")}
        for section in by_header.split_text(page.content):
            for text in by_size.split_text(section.page_content):
                chunks.append(Document(page_content=text, metadata={**source, **section.metadata}))
    return chunks


def build_index():
    chunks = load_chunks()
    store = get_vectorstore()
    store.reset_collection()

    # free tier allows ~100 embeddings a minute, so go in batches and wait between them
    batch = 90
    for i in range(0, len(chunks), batch):
        for attempt in range(3):
            try:
                store.add_documents(chunks[i : i + batch])
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"batch failed ({e}), retrying in a minute...")
                time.sleep(65)
        if i + batch < len(chunks):
            print(f"embedded {i + batch}/{len(chunks)}, waiting for the rate limit...")
            time.sleep(65)
    return len(chunks)


@tool
def search_travel_knowledge_base(query: str) -> str:
    """Search the Singapore travel guide for destination facts (attractions, neighbourhoods, transport, culture, food, itineraries, indoor/outdoor ideas). Not for live weather or currency."""
    docs = get_vectorstore().similarity_search(query, k=config.RAG_TOP_K)
    if not docs:
        return "NO_RESULTS"
    return "\n\n".join(
        f"[{i}] {d.metadata.get('title')} ({d.metadata.get('source_url')})\n{d.page_content}"
        for i, d in enumerate(docs, start=1)
    )
