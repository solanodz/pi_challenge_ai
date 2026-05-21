#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.services.ingest_corpus import ingest_corpus


def main() -> None:
    settings = get_settings()
    if not settings.corpus_path.exists():
        print(f"Error: corpus not found at {settings.corpus_path}")
        print("Place documento.docx in docs/ and run again.")
        sys.exit(1)

    count = ingest_corpus(settings)
    print(f"Ingested {count} chunks into Chroma Cloud")
    print(f"Database: {settings.chroma_database}")
    print(f"Collection: {settings.chroma_collection}")


if __name__ == "__main__":
    main()
