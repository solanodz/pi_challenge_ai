from dataclasses import dataclass

from src.config import Settings
from src.infra.chroma_store import ChromaStore, RetrievalHit
from src.infra.openai_gateway import OpenAIGateway
from src.services.question_splitter import split_questions


@dataclass
class RetrievalResult:
    context: str
    hits: list[RetrievalHit]
    mode: str
    max_distance: float
    question_parts: list[str]


def _merge_context(hits: list[RetrievalHit]) -> str:
    blocks = [f"[{hit.section_title}]\n{hit.document}" for hit in hits]
    return "\n\n".join(blocks)


def retrieve_context(
    question: str,
    chroma: ChromaStore,
    openai: OpenAIGateway,
    settings: Settings,
) -> RetrievalResult | None:
    parts = split_questions(question)
    seen_ids: set[str] = set()
    hits: list[RetrievalHit] = []

    for part in parts:
        hit = chroma.query_top1(openai.embed_one(part))
        if hit is None or hit.chunk_id in seen_ids:
            continue
        seen_ids.add(hit.chunk_id)
        hits.append(hit)

    if not hits:
        return None

    is_compound = len(parts) > 1
    max_distance = max(hit.distance for hit in hits)

    if max_distance > settings.retrieval_distance_max:
        return RetrievalResult(
            context="",
            hits=hits,
            mode="compound" if is_compound else "single",
            max_distance=max_distance,
            question_parts=parts,
        )

    return RetrievalResult(
        context=_merge_context(hits),
        hits=hits,
        mode="compound" if is_compound else "single",
        max_distance=max_distance,
        question_parts=parts,
    )
