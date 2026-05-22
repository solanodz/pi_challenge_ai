"""entry point de la app FastAPI para uvicorn y Docker."""

from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="PI Challenge RAG API",
    description=(
        "Responde preguntas sobre docs/documento.docx usando RAG "
        "(Chroma Cloud + OpenAI)."
    ),
    version="1.0.0",
)

# rutas HTTP: GET /health, POST /ask (ver API.md)
app.include_router(router)
