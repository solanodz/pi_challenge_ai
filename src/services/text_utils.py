import re

from langdetect import DetectorFactory, LangDetectException, detect

# Stable language guesses for the same input (challenge determinism).
DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = frozenset({"es", "en", "pt"})

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


def detect_language(text: str) -> str:
    """Detect es / en / pt using langdetect. Defaults to es if uncertain."""
    stripped = text.strip()
    if not stripped:
        return "es"
    try:
        code = detect(stripped)
    except LangDetectException:
        return "es"
    if code in SUPPORTED_LANGUAGES:
        return code
    if code.startswith("pt"):
        return "pt"
    return "es"


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
