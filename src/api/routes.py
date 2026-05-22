"""rutas http expuestas por la API RAG."""

from chromadb.api.models.Collection import Collection
from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import AnswerResponse, QuestionRequest
from src.config import get_settings
from src.infra.chroma_connection import get_chroma_collection, get_chroma_collection_sync
from src.services.answer_question import answer_question

router = APIRouter(tags=["RAG"])


@router.get("/health")
def health(collection: Collection = Depends(get_chroma_collection)) -> dict:
    """Reporta el estado de la API y la metadata del indice de Chroma (no llama a LLM)."""
    settings = get_settings()
    return {
        "status": "ok",
        "indexed_chunks": collection.count(),
        "corpus_path": str(settings.corpus_path),
        "chroma_database": settings.chroma_database,
        "chroma_collection": settings.chroma_collection,
    }


@router.post("/ask", response_model=AnswerResponse)
def ask(body: QuestionRequest) -> AnswerResponse:
    """
    Responde una pregunta sobre el documento usando RAG.

    El body es validado antes de conectar a Chroma para que json invalido
    (faltantes o campos extra) devuelva 422.
    """
    try:
        collection = get_chroma_collection_sync()
        result = answer_question(body.question, collection=collection)
    except ValueError as exc:
        # API keys o configuracion de Chroma client invalidas.
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        # Archivo del corpus faltante en el disco.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AnswerResponse(
        question=result.question,
        answer=result.answer,
        language=result.language,
        cached=result.cached,
        debug=result.debug,
    )
