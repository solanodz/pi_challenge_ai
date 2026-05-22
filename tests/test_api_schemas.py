import pytest
from pydantic import ValidationError

from src.api.schemas import QuestionRequest


# Test para verificar que se rechazan campos extra
def test_question_request_rejects_extra_fields():
    with pytest.raises(ValidationError) as exc_info:
        QuestionRequest(
            user_name="Solano",
            question="quien es Zara?",
            ej=3,
        )
    errors = exc_info.value.errors()
    assert any(error["type"] == "extra_forbidden" for error in errors)


# Test para verificar que se aceptan solo los campos requeridos
def test_question_request_accepts_required_fields_only():
    body = QuestionRequest(user_name="Solano", question="quien es Zara?")
    assert body.user_name == "Solano"
    assert body.question == "quien es Zara?"
