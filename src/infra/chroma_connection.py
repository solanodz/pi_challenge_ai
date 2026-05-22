"""ConexiON a Chroma Cloud (FastAPI Depends y scripts sync)."""

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import Depends

from src.config import get_settings

_client: ClientAPI | None = None
_collection: Collection | None = None


def get_chroma_client() -> ClientAPI:
    """Devuelve un CloudClient reutilizado por proceso."""
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.chroma_api_key:
            raise ValueError("CHROMA_API_KEY is not set")
        _client = chromadb.CloudClient(
            api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database,
        )
    return _client


def _bind_collection(client: ClientAPI) -> Collection:
    """Obtiene o crea la colección configurada en .env"""
    global _collection
    if _collection is None:
        settings = get_settings()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection,
            # L2 coincide con la metrica usada para calibrar RETRIEVAL_DISTANCE_MAX.
            metadata={"hnsw:space": "l2"},
        )
    return _collection


def get_chroma_collection(
    client: ClientAPI = Depends(get_chroma_client),
) -> Collection:
    """Inyección FastAPI: coleccion Chroma para rutas http"""
    return _bind_collection(client)


def get_chroma_collection_sync() -> Collection:
    """Misma colección que FastAPI, para scripts (ingest, /ask sin Depends)."""
    return _bind_collection(get_chroma_client())


def reset_chroma_collection() -> Collection:
    """Borra y recrea la colección (ingest limpio)."""
    global _collection
    settings = get_settings()
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection)
    except Exception:
        # La colección puede no existir en el primer ingest.
        pass
    _collection = None
    return get_chroma_collection_sync()
