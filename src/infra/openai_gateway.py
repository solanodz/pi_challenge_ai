"""OpenAI para embeddings y chat completions"""

from openai import OpenAI

from src.config import Settings


class OpenAIGateway:
    """Encapsula las llamadas a la API de OpenAI usadas por el RAG."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para uno o mas textos."""
        response = self._client.embeddings.create(
            model=self._settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def embed_one(self, text: str) -> list[float]:
        """Embedding de una sola pregunta o chunk."""
        return self.embed([text])[0]

    def chat(self, system: str, user: str) -> str:
        """Completa el prompt; temperature=0 para respuestas deterministicas"""
        response = self._client.chat.completions.create(
            model=self._settings.openai_chat_model,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (response.choices[0].message.content or "").strip()
