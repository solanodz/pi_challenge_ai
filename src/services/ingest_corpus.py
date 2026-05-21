from chromadb.api.models.Collection import Collection

from src.config import Settings, get_settings
from src.infra.chroma_connection import get_chroma_collection_sync, reset_chroma_collection
from src.infra.chroma_store import ChromaStore
from src.infra.docx_reader import read_sections
from src.infra.openai_gateway import OpenAIGateway


def ingest_corpus(
    settings: Settings | None = None,
    reset: bool = True,
    collection: Collection | None = None,
) -> int:
    settings = settings or get_settings()
    sections = read_sections(settings.corpus_path)
    openai = OpenAIGateway(settings)
    if collection is None:
        collection = reset_chroma_collection() if reset else get_chroma_collection_sync()
    elif reset:
        collection = reset_chroma_collection()
    chroma = ChromaStore(collection)

    ids = [section.chunk_id for section in sections]
    documents = [section.text for section in sections]
    metadatas = [
        {"section_title": section.section_title, "chunk_id": section.chunk_id}
        for section in sections
    ]
    embeddings = openai.embed(documents)
    chroma.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return len(sections)
