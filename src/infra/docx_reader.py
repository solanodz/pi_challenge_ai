"""Lectura del corpus Word y división en secciones (chunks)"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from docx import Document

# Chroma Cloud limita el tamaño del ID; usamos slugs cortos por título.
MAX_CHUNK_ID_BYTES = 120


@dataclass
class SectionChunk:
    """Una seccion del documento lista para hacer el embedding e indexar."""

    chunk_id: str
    section_title: str
    text: str


def _slugify(title: str) -> str:
    """Convierte un título en un id seguro para Chroma."""
    normalized = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore") # Convierte el titulo a ascii ignorando los caracteres no ascii.
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-") # Reemplaza los caracteres no ascii por un guion.
    return slug or "section" # Si el slug es vacio devuelve "section"


def _short_chunk_id(title: str, index: int) -> str:
    """Slug del título o fallback numerico si excede el límite de bytes"""
    slug = _slugify(title)
    if len(slug.encode("utf-8")) <= MAX_CHUNK_ID_BYTES:
        return slug
    return f"chunk-{index + 1}"


def _split_title_body(paragraph_text: str) -> tuple[str, str]:
    """Separa 'Título: cuerpo' en una sola línea."""
    text = paragraph_text.strip()
    if ": " in text:
        title, body = text.split(": ", 1)
        return title.strip(), body.strip()
    return text, ""


def _paragraph_is_title_only(paragraph) -> bool:
    """True si el párrafo es solo un título en negrita (formato A)"""
    text = paragraph.text.strip()
    if not text:
        return False
    runs_with_text = [run for run in paragraph.runs if run.text.strip()]
    if not runs_with_text:
        return False
    return all(run.bold for run in runs_with_text)


def read_sections(docx_path: Path) -> list[SectionChunk]:
    """
    Lee el doc y devuelve una lista de secciones.

    Soporta dos formatos:
    - A: párrafo título (bold) + párrafos de cuerpo
    - B: un párrafo Título: cuerpo (formato del corpus del challenge)
    """
    if not docx_path.exists():
        raise FileNotFoundError(f"Corpus not found: {docx_path}")

    document = Document(docx_path)
    sections: list[SectionChunk] = []

    current_title: str | None = None
    body_parts: list[str] = []

    def flush_title_body() -> None:
        nonlocal current_title, body_parts
        if not current_title:
            return
        body = " ".join(part.strip() for part in body_parts if part.strip())
        full_text = f"{current_title}: {body}".strip(": ").strip()
        index = len(sections)
        sections.append(
            SectionChunk(
                chunk_id=_short_chunk_id(current_title, index),
                section_title=current_title,
                text=full_text if body else current_title,
            )
        )
        current_title = None
        body_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if _paragraph_is_title_only(paragraph): # Si el párrafo es solo un título en negrita (formato A)
            flush_title_body()
            current_title = text
            body_parts = []
        elif current_title is not None: # Si el párrafo es un cuerpo (formato B)
            body_parts.append(text)
        else:
            title, body = _split_title_body(text) # Si el párrafo es un título y un cuerpo (formato B)
            full_text = f"{title}: {body}".strip(": ").strip() if body else text
            index = len(sections)
            sections.append(
                SectionChunk(
                    chunk_id=_short_chunk_id(title, index),
                    section_title=title,
                    text=full_text,
                )
            )

    flush_title_body()

    if not sections:
        raise ValueError(f"No sections found in {docx_path}")

    return sections
