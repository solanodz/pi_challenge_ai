from src.services.text_utils import detect_language


def test_spanish_with_por_que_not_portuguese():
    question = (
        "que pasa cada año en un pueblo? quien es Alex? "
        "a que se le llama la flor magica y por que lucha la humanidad?"
    )
    assert detect_language(question) == "es"


def test_spanish_simple():
    assert detect_language("Quien es Zara?") == "es"


def test_english():
    assert detect_language("What is the name of the magical flower?") == "en"


def test_portuguese():
    assert detect_language("Quem é Alex e por que a humanidade luta?") == "pt"
