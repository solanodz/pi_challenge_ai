#!/usr/bin/env python3
"""Ingest corpus (optional) and start the FastAPI server locally."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.services.ingest_corpus import ingest_corpus


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run corpus ingest (optional) and start the RAG API locally."
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip ingest and only start the API (index must already exist in Chroma).",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Uvicorn host (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=8000, help="Uvicorn port (default: 8000).")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable uvicorn auto-reload for development.",
    )
    args = parser.parse_args()

    settings = get_settings()

    if not args.skip_ingest:
        if not settings.corpus_path.exists():
            print(f"Error: corpus not found at {settings.corpus_path}")
            print("Place documento.docx in docs/ and run again.")
            sys.exit(1)
        count = ingest_corpus(settings)
        print(f"Ingested {count} chunks into Chroma Cloud")
        print(f"Database: {settings.chroma_database}")
        print(f"Collection: {settings.chroma_collection}")
    else:
        print("Skipping ingest (--skip-ingest).")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    if args.reload:
        cmd.append("--reload")

    display_host = "localhost" if args.host == "0.0.0.0" else args.host
    print(f"Starting API at http://{display_host}:{args.port}")
    raise SystemExit(subprocess.run(cmd, cwd=ROOT, check=False).returncode)


if __name__ == "__main__":
    main()
