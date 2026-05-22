"""
División de mensajes compuestos en subpreguntas.

Solo usa señales estructurales (puntuación, saltos de línea)
"""

import re

MIN_PART_CHARS = 4 

_QUESTION_MARK_BOUNDARY = re.compile(r"[?!]+\s*") # Signo de pregunta/exclamacion
_SEMICOLON_BOUNDARY = re.compile(r"\s*;\s*") # Punto y coma
_NEWLINE_BOUNDARY = re.compile(r"\n+") # Salto de linea


def _normalize_part(part: str) -> str:
    """Limpia espacios, comas y un label inicial si existe."""
    text = part.strip(" ,.")
    text = re.sub(r"^[;,\s]+", "", text)
    return text


def _valid_parts(parts: list[str]) -> list[str]:
    return [p for p in (_normalize_part(x) for x in parts) if len(p) >= MIN_PART_CHARS]


def _split_if_multiple(text: str, pattern: re.Pattern[str]) -> list[str] | None:
    """Parte solo si el patrón produce al menos dos subpreguntas válidas"""
    if not pattern.search(text):
        return None
    parts = _valid_parts(pattern.split(text))
    return parts if len(parts) > 1 else None


def split_questions(message: str) -> list[str]:
    """
    Devuelve una o más subpreguntas para retrieval.

    Estrategias para separar las preguntas compuestas:
    1. Signo de pregunta/exclamacion: "Q1? Q2?"
    2. Punto y coma: "Q1; Q2"
    3. Saltos de linea: "Q1\nQ2"
    """
    raw = message.strip()
    if not raw:
        return []

    for pattern in (_QUESTION_MARK_BOUNDARY, _SEMICOLON_BOUNDARY, _NEWLINE_BOUNDARY):
        parts = _split_if_multiple(raw, pattern)
        if parts:
            return parts

    return [raw]
