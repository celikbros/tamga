from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from scripts.compare_tokenizers import boundary_score, token_boundaries
from tr_tokenizer.baseline_bpe import encode_bpe, load_bpe, save_bpe, train_bpe


def test_toy_bpe_train_and_encode_returns_tokens():
    model = train_bpe(["Arabalarımızdan indiler.", "Geldim."], vocab_size=40)
    tokens = encode_bpe("Arabalarımızdan indiler.", model)

    assert model["merges"]
    assert tokens


def test_toy_bpe_save_and_load_round_trip():
    model = train_bpe(["Geldim.", "Gittim."], vocab_size=30)
    path = Path("artifacts") / f"tr_tokenizer_bpe_{uuid4().hex}.json"

    try:
        save_bpe(model, path)
        loaded = load_bpe(path)
    finally:
        if path.exists():
            path.unlink()

    assert loaded == model


def test_token_boundaries_simple_example():
    assert token_boundaries(["▁Gel", "+di", "+m", "."]) == {3, 5, 6}


def test_boundary_score_simple_example():
    score = boundary_score(
        predicted_tokens=["▁Geldi", "m", "."],
        gold_tokens=["▁Gel", "+di", "+m", "."],
    )

    assert score.correct == 2
    assert score.predicted == 2
    assert score.gold == 3
