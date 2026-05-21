from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    user_name: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class AnswerResponse(BaseModel):
    answer: str
    language: str
    cached: bool
    debug: dict
