from pydantic import BaseModel, ConfigDict, Field


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_name: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    language: str
    cached: bool
    debug: dict
