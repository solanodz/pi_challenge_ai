import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from docx import Document

# Chroma Cloud free tier limits ID size (bytes); keep ids short.
MAX_CHUNK_ID_BYTES = 120


@dataclass
class SectionChunk:
    chunk_id: str
    section_title: str
    text: str


def _slugify(title: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "section"


def _short_chunk_id(title: str, index: int) -> str:
    slug = _slugify(title)
    if len(slug.encode("utf-8")) <= MAX_CHUNK_ID_BYTES:
        return slug
    return f"chunk-{index + 1}"


def _split_title_body(paragraph_text: str) -> tuple[str, str]:
    text = paragraph_text.strip()
    if ": " in text:
        title, body = text.split(": ", 1)
        return title.strip(), body.strip()
    return text, ""


def _paragraph_is_title_only(paragraph) -> bool:
    text = paragraph.text.strip()
    if not text:
        return False
    runs_with_text = [run for run in paragraph.runs if run.text.strip()]
    if not runs_with_text:
        return False
    return all(run.bold for run in runs_with_text)


def read_sections(docx_path: Path) -> list[SectionChunk]:
    if not docx_path.exists():
        raise FileNotFoundError(f"Corpus not found: {docx_path}")

    document = Document(docx_path)
    sections: list[SectionChunk] = []

    # Format A: title paragraph (bold) + body paragraph(s)
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
        if _paragraph_is_title_only(paragraph):
            flush_title_body()
            current_title = text
            body_parts = []
        elif current_title is not None:
            body_parts.append(text)
        else:
            # Format B: single paragraph "Title: body" (this corpus)
            title, body = _split_title_body(text)
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
