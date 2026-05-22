"""
Split a user message into independent questions using structural cues only.

We do not match topic-specific words (e.g. "quien", "Zara"). Boundaries come from
punctuation and layout—the same signals users expect in a Q&A API.
"""

import re

MIN_PART_CHARS = 4

# Optional leading label: "decime: ...", "note: ..." (single prefix, any word)
_LEADING_LABEL = re.compile(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+:\s*", re.IGNORECASE)

_QUESTION_MARK_BOUNDARY = re.compile(r"[?!]+\s*")
_SEMICOLON_BOUNDARY = re.compile(r"\s*;\s*")
_NEWLINE_BOUNDARY = re.compile(r"\n+")


def _normalize_part(part: str) -> str:
    text = part.strip(" ,.")
    text = re.sub(r"^[;,\s]+", "", text)
    text = _LEADING_LABEL.sub("", text, count=1).strip()
    return text


def _valid_parts(parts: list[str]) -> list[str]:
    return [p for p in (_normalize_part(x) for x in parts) if len(p) >= MIN_PART_CHARS]


def _split_if_multiple(text: str, pattern: re.Pattern[str]) -> list[str] | None:
    if not pattern.search(text):
        return None
    parts = _valid_parts(pattern.split(text))
    return parts if len(parts) > 1 else None


def split_questions(message: str) -> list[str]:
    """
    Devolver una o mas preguntas para recuperar.

    Estrategias para separar las preguntas compuestas:
    1. Signo de pregunta/exclamacion: "Q1? Q2?"
    2. Punto y coma: "Q1; Q2"
    3. Saltos de linea: "Q1\\nQ2"
    """
    raw = message.strip()
    if not raw:
        return []

    for pattern in (_QUESTION_MARK_BOUNDARY, _SEMICOLON_BOUNDARY, _NEWLINE_BOUNDARY):
        parts = _split_if_multiple(raw, pattern)
        if parts:
            return parts

    return [raw]
