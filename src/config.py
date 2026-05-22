"""Configuraciones de la aplicacion cargadas desde .env"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# directorio raiz del proyecto (padre de `src/`).
ROOT_DIR = Path(__file__).resolve().parents[1]

# carga el .env una vez al importar el modulo para que scripts y uvicorn compartan la misma config.
load_dotenv(ROOT_DIR / ".env")


def _resolve_path(raw: str) -> Path:
    """Resuelve las rutas del corpus relativas a la raiz del proyecto a menos que ya sean absolutas."""
    path = Path(raw)
    return path if path.is_absolute() else ROOT_DIR / path


@lru_cache
def get_settings() -> "Settings":
    """Devuelve una instancia de settings (una por proceso)"""
    return Settings()


class Settings:
    """Configuracion de runtime para OpenAI, Chroma Cloud, ruta del corpus y ajuste de RAG.
    Atributos:
    - openai_api_key: API key de OpenAI
    - corpus_path: ruta del corpus
    - chroma_api_key: API key de Chroma Cloud
    - chroma_tenant: tenant de Chroma Cloud
    - chroma_database: database de Chroma Cloud
    - chroma_collection: collection de Chroma Cloud
    - openai_chat_model: modelo de chat de OpenAI
    - openai_embedding_model: modelo de embedding de OpenAI (...-3-small)
    - retrieval_distance_max: distancia maxima de retrieval
    - prompts_dir: ruta de los prompts
    """
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
        self.corpus_path = _resolve_path(
            os.environ.get("CORPUS_PATH", "docs/documento.docx")
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
            os.environ.get("RETRIEVAL_DISTANCE_MAX", "1.77")
        )
        # los templates de prompts están junto a este modulo (`src/prompts/`).
        self.prompts_dir = Path(__file__).resolve().parent / "prompts"
