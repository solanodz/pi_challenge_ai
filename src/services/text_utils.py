import re

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


def detect_language(question: str) -> str:
    text = question.lower()
    english_markers = (
        r"\b(what|who|where|when|how|which|why|did|does|is|are|the|name)\b"
    )
    portuguese_markers = (
        r"\b(quem|onde|quando|como|qual|por que|não|voce|você|uma|está)\b"
    )
    if re.search(english_markers, text):
        return "en"
    if re.search(portuguese_markers, text) or re.search(r"[ãõç]", text):
        return "pt"
    return "es"


def not_in_document_answer(language: str) -> str:
    return NOT_IN_DOCUMENT.get(language, NOT_IN_DOCUMENT["es"])


def cache_key(question: str, language: str) -> str:
    return f"{language}:{normalize_question(question)}"


def answer_matches_language(answer: str, language: str) -> bool:
    if answer in NOT_IN_DOCUMENT.values():
        return answer == not_in_document_answer(language)
    return detect_language(answer) == language
