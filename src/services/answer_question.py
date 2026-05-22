from dataclasses import dataclass

from chromadb.api.models.Collection import Collection

from src.config import Settings, get_settings
from src.infra.chroma_connection import get_chroma_collection_sync
from src.infra.chroma_store import ChromaStore
from src.infra.memory_cache import MemoryCache
from src.infra.openai_gateway import OpenAIGateway
from src.infra.prompt_loader import load_answer_prompt
from src.services.retrieval import retrieve_context
from src.services.text_utils import (
    ANSWER_LANGUAGE_LABEL,
    answer_matches_language,
    cache_key,
    detect_language,
    is_not_in_document_answer,
    not_in_document_answer,
)

_cache = MemoryCache()


@dataclass
class AnswerResult:
    question: str
    answer: str
    language: str
    cached: bool
    debug: dict


def _cache_answer(key: str, answer: str, language: str) -> None:
    if not is_not_in_document_answer(answer, language):
        _cache.set(key, answer)


def _load_prompts(settings: Settings) -> tuple[str, str]:
    return load_answer_prompt(settings.prompts_dir)


def answer_question(
    question: str,
    settings: Settings | None = None,
    collection: Collection | None = None,
) -> AnswerResult:
    settings = settings or get_settings()
    language = detect_language(question)
    key = cache_key(question, language)

    cached_answer = _cache.get(key)
    if cached_answer is not None and answer_matches_language(cached_answer, language):
        return AnswerResult(
            question=question,
            answer=cached_answer,
            language=language,
            cached=True,
            debug={"cache_hit": True},
        )

    if collection is None:
        collection = get_chroma_collection_sync()
    chroma = ChromaStore(collection)
    if chroma.count() == 0:
        answer = not_in_document_answer(language)
        return AnswerResult(
            question=question,
            answer=answer,
            language=language,
            cached=False,
            debug={"reason": "index_empty"},
        )

    openai = OpenAIGateway(settings)
    retrieval = retrieve_context(question, chroma, openai, settings)

    if retrieval is None:
        answer = not_in_document_answer(language)
        return AnswerResult(
            question=question,
            answer=answer,
            language=language,
            cached=False,
            debug={"reason": "no_hit"},
        )

    debug = {
        "retrieval_mode": retrieval.mode,
        "question_parts": retrieval.question_parts,
        "chunk_ids": [hit.chunk_id for hit in retrieval.hits],
        "section_titles": [hit.section_title for hit in retrieval.hits],
        "retrieval_distance": retrieval.max_distance,
        "retrieval_threshold": settings.retrieval_distance_max,
    }
    if len(retrieval.hits) == 1:
        debug["chunk_id"] = retrieval.hits[0].chunk_id
        debug["section_title"] = retrieval.hits[0].section_title

    if retrieval.max_distance > settings.retrieval_distance_max:
        answer = not_in_document_answer(language)
        debug["reason"] = "below_threshold"
        return AnswerResult(
            question=question,
            answer=answer,
            language=language,
            cached=False,
            debug=debug,
        )

    system_prompt, user_template = _load_prompts(settings)
    answer_language = ANSWER_LANGUAGE_LABEL[language]
    user_prompt = user_template.format(
        context=retrieval.context,
        question=question,
        answer_language=answer_language,
    )
    system_prompt = system_prompt.format(answer_language=answer_language)
    answer = openai.chat(system=system_prompt, user=user_prompt)
    if not answer_matches_language(answer, language):
        retry_user = (
            f"{user_prompt}\n\n"
            f"IMPORTANT: Rewrite the answer entirely in {answer_language}. "
            "Do not use Spanish if the question is in English."
        )
        answer = openai.chat(system=system_prompt, user=retry_user)
    _cache_answer(key, answer, language)

    return AnswerResult(
        question=question,
        answer=answer,
        language=language,
        cached=False,
        debug=debug,
    )
