from __future__ import annotations

from tr_tokenizer.boundary_weighted_bpe import (
    encode_boundary_weighted_bpe,
    morph_boundaries,
    train_boundary_weighted_bpe,
)


def test_morph_boundaries_follow_teacher_segments():
    assert morph_boundaries("Arabalarımızdan")


def test_boundary_lambda_reduces_crossing_merges():
    lines = ["Arabalarımızdan haber aldık."] * 50
    plain = train_boundary_weighted_bpe(
        lines,
        vocab_size=80,
        boundary_lambda=0.0,
        min_score=2.0,
    )
    biased = train_boundary_weighted_bpe(
        lines,
        vocab_size=80,
        boundary_lambda=100.0,
        min_score=2.0,
    )

    plain_crossing = sum(
        1 for row in plain["merge_stats"] if row["crossing_count"] > 0
    )
    biased_crossing = sum(
        1 for row in biased["merge_stats"] if row["crossing_count"] > 0
    )

    assert biased_crossing < plain_crossing


def test_boundary_weighted_bpe_encodes_text():
    model = train_boundary_weighted_bpe(
        ["Arabalarımızdan haber aldık."],
        vocab_size=40,
        boundary_lambda=4.0,
    )

    tokens = encode_boundary_weighted_bpe("Arabalarımızdan haber aldık.", model)

    assert tokens
