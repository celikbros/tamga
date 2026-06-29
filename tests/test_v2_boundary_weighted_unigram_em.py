import math

import pytest
from sentencepiece import sentencepiece_model_pb2

from scripts.materialize_v2_boundary_weighted_unigram_em import (
    Entry,
    WeightedVocab,
    expected_counts_for_segment,
    logaddexp,
    train_iteration,
)
from scripts.materialize_v2_score_shifted_sp_model import Segment


def make_vocab(entries: list[tuple[str, float]]) -> WeightedVocab:
    by_surface = {}
    by_start_surface = {}
    for piece, score in entries:
        word_start = piece.startswith("\u2581")
        surface = piece[1:] if word_start else piece
        entry = Entry(piece=piece, surface=surface, score=score, word_start=word_start)
        if word_start:
            by_start_surface[surface] = entry
        else:
            by_surface[surface] = entry
    return WeightedVocab(
        entries_by_surface=by_surface,
        start_entries_by_surface=by_start_surface,
        max_entry_len=max((len(entry.surface) for entry in by_surface.values()), default=0),
        max_start_entry_len=max(
            (len(entry.surface) for entry in by_start_surface.values()), default=0
        ),
    )


def test_logaddexp_handles_negative_infinity():
    assert logaddexp(float("-inf"), -3.0) == -3.0
    assert logaddexp(-3.0, float("-inf")) == -3.0
    assert logaddexp(math.log(2.0), math.log(3.0)) == pytest.approx(math.log(5.0))


def test_expected_counts_split_between_crossing_and_boundary_aligned_paths():
    vocab = make_vocab(
        [
            ("abcd", 0.0),
            ("ab", 0.0),
            ("cd", 0.0),
        ]
    )
    segment = Segment(surface="abcd", soft_boundaries=(2,))

    counts, log_z, expected_crossings = expected_counts_for_segment(
        segment,
        vocab=vocab,
        boundary_lambda=0.0,
    )

    assert log_z == pytest.approx(math.log(2.0))
    assert counts["abcd"] == pytest.approx(0.5)
    assert counts["ab"] == pytest.approx(0.5)
    assert counts["cd"] == pytest.approx(0.5)
    assert expected_crossings == pytest.approx(0.5)


def test_boundary_lambda_prefers_boundary_aligned_path():
    vocab = make_vocab(
        [
            ("abcd", 0.0),
            ("ab", 0.0),
            ("cd", 0.0),
        ]
    )
    segment = Segment(surface="abcd", soft_boundaries=(2,))

    counts, _, expected_crossings = expected_counts_for_segment(
        segment,
        vocab=vocab,
        boundary_lambda=10.0,
    )

    assert counts["abcd"] < 0.001
    assert counts["ab"] > 0.999
    assert counts["cd"] > 0.999
    assert expected_crossings < 0.001


def test_word_start_piece_matches_only_at_segment_start():
    vocab = make_vocab(
        [
            ("\u2581ab", 0.0),
            ("ab", 0.0),
            ("c", 0.0),
        ]
    )

    assert [entry.piece for entry in vocab.candidates_at("abc", 0)] == [
        "ab",
        "\u2581ab",
    ]
    assert [entry.piece for entry in vocab.candidates_at("abc", 1)] == []


def test_train_iteration_updates_scores_without_protobuf_key_error(tmp_path):
    model = sentencepiece_model_pb2.ModelProto()
    for piece_name, score in [
        ("k", -3.0),
        ("i", -3.0),
        ("t", -3.0),
        ("a", -3.0),
        ("p", -3.0),
        ("l", -3.0),
        ("r", -3.0),
        ("kitap", -1.0),
        ("lar", -1.0),
        ("kitaplar", -0.5),
    ]:
        piece = model.pieces.add()
        piece.piece = piece_name
        piece.score = score

    train_path = tmp_path / "train.txt"
    train_path.write_text("kitaplar\n", encoding="utf-8")

    stats = train_iteration(
        model=model,
        train_path=train_path,
        boundary_lambda=1.0,
        max_lines=1,
        progress=0,
        iteration=1,
        score_floor=-30.0,
    )

    assert stats.lines == 1
    assert stats.changed_piece_scores > 0
    assert stats.expected_crossings >= 0.0
