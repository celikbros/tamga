import pytest

from tr_tokenizer.normalizer import normalize_text, turkish_lower


def test_normalize_text_collapses_space_and_apostrophe():
    text = "  Türkiye’den \n\t geldim  "

    assert normalize_text(text) == "Türkiye'den geldim"


def test_normalize_text_preserves_smart_double_quotes():
    assert normalize_text("“Merhaba,” dedi.") == "“Merhaba,” dedi."


def test_normalize_text_preserves_modifier_apostrophe_letters():
    assert normalize_text("Oʻzbekcha sanʼat") == "Oʻzbekcha sanʼat"


def test_normalize_text_preserves_dash_width():
    assert normalize_text("Қазақстан — Алматы") == "Қазақстан — Алматы"


def test_turkish_lower_handles_dotted_and_dotless_i():
    assert turkish_lower("I İ ISPARTA İZMİR") == "ı i ısparta izmir"


def test_normalize_text_rejects_non_string():
    with pytest.raises(TypeError):
        normalize_text(None)  # type: ignore[arg-type]
