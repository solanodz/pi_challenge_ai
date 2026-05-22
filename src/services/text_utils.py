import re
from functools import lru_cache

from lingua import Language, LanguageDetectorBuilder

SUPPORTED_LANGUAGES = frozenset({"es", "en", "pt"})

LINGUA_TO_CODE = {
    Language.SPANISH: "es",
    Language.ENGLISH: "en",
    Language.PORTUGUESE: "pt",
}

NOT_IN_DOCUMENT = {
    "es": "La información solicitada no figura en el documento proporcionado 📄.",
    "en": "The requested information does not appear in the provided document 📄.",
    "pt": "A informação solicitada não consta no documento fornecido 📄.",
}

ANSWER_LANGUAGE_LABEL = {
    "es": "español",
    "en": "inglés (English)",
    "pt": "portugués (português)",
}


def normalize_question(question: str) -> str:
    normalized = question.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.rstrip("?¿").rstrip()
    return normalized


@lru_cache(maxsize=1)
def _language_detector():
    return (
        LanguageDetectorBuilder.from_languages(
            Language.SPANISH,
            Language.ENGLISH,
            Language.PORTUGUESE,
        )
        .with_preloaded_language_models()
        .build()
    )


def detect_language(text: str) -> str:
    """Detect es / en / pt with Lingua (restricted to challenge languages)."""
    stripped = text.strip()
    if not stripped:
        return "es"
    detected = _language_detector().detect_language_of(stripped)
    if detected is None:
        return "es"
    return LINGUA_TO_CODE.get(detected, "es")


def not_in_document_answer(language: str) -> str:
    return NOT_IN_DOCUMENT.get(language, NOT_IN_DOCUMENT["es"])


def is_not_in_document_answer(answer: str, language: str) -> bool:
    return answer == not_in_document_answer(language)


def cache_key(question: str, language: str) -> str:
    return f"{language}:{normalize_question(question)}"


def answer_matches_language(answer: str, language: str) -> bool:
    if answer in NOT_IN_DOCUMENT.values():
        return answer == not_in_document_answer(language)
    return detect_language(answer) == language
