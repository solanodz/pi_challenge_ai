from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="PI Challenge RAG API",
    description="Answers questions about documento.docx using RAG.",
    version="1.0.0",
)
app.include_router(router)
