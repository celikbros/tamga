from __future__ import annotations

import pytest

from tr_tokenizer.external_baselines import (
    encode_huggingface,
    encode_sentencepiece,
    encode_unicode_chars,
    parse_named_spec,
)


def test_unicode_char_baseline_marks_word_starts() -> None:
    result = encode_unicode_chars("Ali geldi.")

    assert result.status == "ok"
    assert result.tokens[:3] == ["▁A", "l", "i"]
    assert "▁g" in result.tokens
    assert result.tokens[-1] == "."


def test_parse_named_spec() -> None:
    assert parse_named_spec("qwen=Qwen/Qwen2.5-0.5B") == (
        "qwen",
        "Qwen/Qwen2.5-0.5B",
    )


@pytest.mark.parametrize("spec", ["qwen", "=model", "name="])
def test_parse_named_spec_rejects_invalid_input(spec: str) -> None:
    with pytest.raises(ValueError):
        parse_named_spec(spec)


def test_huggingface_baseline_skips_when_dependency_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tr_tokenizer.external_baselines.importlib.util.find_spec",
        lambda name: None if name == "transformers" else object(),
    )

    result = encode_huggingface(
        "Geldim.",
        model_id="unused",
        name="hf_missing",
        local_files_only=True,
    )

    assert result.status == "skipped"
    assert "transformers" in result.reason


def test_sentencepiece_baseline_skips_when_dependency_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tr_tokenizer.external_baselines.importlib.util.find_spec",
        lambda name: None if name == "sentencepiece" else object(),
    )

    result = encode_sentencepiece(
        "Geldim.",
        model_path="missing.model",
        name="sp_missing",
    )

    assert result.status == "skipped"
    assert "sentencepiece" in result.reason
