import pytest

from tr_tokenizer.normalizer import normalize_text, turkish_lower


def test_normalize_text_collapses_space_and_apostrophe():
    text = "  Türkiye’den \n\t geldim  "

    assert normalize_text(text) == "Türkiye'den geldim"


def test_turkish_lower_handles_dotted_and_dotless_i():
    assert turkish_lower("I İ ISPARTA İZMİR") == "ı i ısparta izmir"


def test_normalize_text_rejects_non_string():
    with pytest.raises(TypeError):
        normalize_text(None)  # type: ignore[arg-type]
