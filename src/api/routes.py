from chromadb.api.models.Collection import Collection
from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import AnswerResponse, QuestionRequest
from src.config import get_settings
from src.infra.chroma_connection import get_chroma_collection, get_chroma_collection_sync
from src.infra.chroma_store import ChromaStore
from src.services.answer_question import answer_question

router = APIRouter()


@router.get("/health")
def health(collection: Collection = Depends(get_chroma_collection)) -> dict:
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
    try:
        collection = get_chroma_collection_sync()
        result = answer_question(body.question, collection=collection)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AnswerResponse(
        question=result.question,
        answer=result.answer,
        language=result.language,
        cached=result.cached,
        debug=result.debug,
    )
