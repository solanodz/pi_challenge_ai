import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@lru_cache
def get_settings() -> "Settings":
    return Settings()


class Settings:
    openai_api_key: str
    corpus_path: Path
    chroma_api_key: str
    chroma_tenant: str
    chroma_database: str
    chroma_collection: str
    openai_chat_model: str
    openai_embedding_model: str
    retrieval_distance_max: float
    prompts_dir: Path

    def __init__(self) -> None:
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.corpus_path = ROOT_DIR / os.environ.get(
            "CORPUS_PATH", "docs/documento.docx"
        )
        self.chroma_api_key = os.environ.get("CHROMA_API_KEY", "")
        self.chroma_tenant = os.environ.get("CHROMA_TENANT", "")
        self.chroma_database = os.environ.get("CHROMA_DATABASE", "pi_challenge_AI")
        self.chroma_collection = os.environ.get("CHROMA_COLLECTION", "corpus")
        self.openai_chat_model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.openai_embedding_model = os.environ.get(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self.retrieval_distance_max = float(
            os.environ.get("RETRIEVAL_DISTANCE_MAX", "1.25")
        )
        self.prompts_dir = Path(__file__).resolve().parent / "prompts"
