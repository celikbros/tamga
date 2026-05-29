from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from scripts.train_sentencepiece_baselines import train_sentencepiece
from tr_tokenizer.external_baselines import encode_sentencepiece


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("sentencepiece") is None,
    reason="sentencepiece optional dependency is not installed",
)


def test_train_sentencepiece_baseline_and_encode(tmp_path: Path) -> None:
    corpus = tmp_path / "tr_demo.txt"
    corpus.write_text(
        "\n".join(
            [
                "Geldim ve kitabımı aldım.",
                "Türkiye'den İstanbul'a gittim.",
                "README.md dosyasını açtım.",
                "Gelicem birazdan.",
            ]
        ),
        encoding="utf-8",
    )

    model_path, vocab_path = train_sentencepiece(
        corpus,
        tmp_path / "sp_bpe_demo",
        vocab_size=64,
        model_type="bpe",
    )

    assert model_path.exists()
    assert vocab_path.exists()

    encoded = encode_sentencepiece(
        "Geldim.",
        model_path=model_path,
        name="sp_bpe_demo",
    )
    assert encoded.status == "ok"
    assert encoded.tokens
