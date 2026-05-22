"""modelos pydantic para las peticiones y respuestas HTTP."""

from pydantic import BaseModel, ConfigDict, Field

class QuestionRequest(BaseModel):
    """Body para POST /ask (contrato del challenge: user_name + question)."""

    model_config = ConfigDict(extra="forbid")

    user_name: str = Field(..., min_length=1, description="Nombre de usuario.")
    question: str = Field(
        ...,
        min_length=1,
        description="Pregunta sobre el documento del corpus.",
    )


class AnswerResponse(BaseModel):
    """Respuesta exitosa de POST /ask."""

    question: str = Field(..., description="Echo de la pregunta enviada.")
    answer: str = Field(..., description="Respuesta del LLM (una oracion, tercera persona, emojis).")
    language: str = Field(..., description="Idioma detectado: es, en, o pt.")
    cached: bool = Field(
        ...,
        description="True cuando la respuesta fue servida desde la cache en memoria.",
    )
    debug: dict = Field(
        ...,
        description="Metadata de retrieval, flag de cache hit, o razon de rechazo.",
    )
