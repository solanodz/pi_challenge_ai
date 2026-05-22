from src.services.question_splitter import split_questions


def test_single_question_with_mark():
    assert split_questions("Quien es Zara?") == ["Quien es Zara?"]


def test_three_questions_by_question_mark():
    message = "que pasa cada año en un pueblo? quien es Alex? a que se le llama la flor magica?"
    assert split_questions(message) == [
        "que pasa cada año en un pueblo",
        "quien es Alex",
        "a que se le llama la flor magica",
    ]


def test_semicolon_separated():
    assert split_questions("Quien es Zara?; quien es Alex?") == [
        "Quien es Zara",
        "quien es Alex",
    ]


def test_newline_separated():
    assert split_questions("Quien es Zara?\nquien es Alex?") == [
        "Quien es Zara",
        "quien es Alex",
    ]


def test_strips_leading_label():
    message = "decime: que pasa? quien es Alex?"
    assert split_questions(message) == ["que pasa", "quien es Alex"]


def test_no_boundary_stays_single():
    # Without ? ; or newline we cannot infer multiple questions reliably.
    message = "quien es Alex y a que se le llama la flor magica"
    assert split_questions(message) == [message]
