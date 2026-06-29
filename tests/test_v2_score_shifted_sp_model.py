import pytest
from sentencepiece import sentencepiece_model_pb2

from scripts.materialize_v2_score_shifted_sp_model import (
    PieceStats,
    adjust_model_scores,
    crosses_boundary,
    piece_surface,
)


def test_piece_surface_removes_sentencepiece_word_start_marker():
    assert piece_surface("▁kitap") == "kitap"
    assert piece_surface("lar") == "lar"


def test_crosses_boundary_only_for_internal_boundary():
    assert crosses_boundary(0, 5, (2,))
    assert not crosses_boundary(0, 2, (2,))
    assert not crosses_boundary(2, 5, (2,))


def test_adjust_model_scores_penalizes_high_crossing_piece():
    model = sentencepiece_model_pb2.ModelProto()
    piece = model.pieces.add()
    piece.piece = "▁kitaplar"
    piece.score = -2.0
    clean_piece = model.pieces.add()
    clean_piece.piece = "▁kitap"
    clean_piece.score = -1.0

    adjustments = adjust_model_scores(
        model,
        {
            "▁kitaplar": PieceStats(count=10, crossing_count=8),
            "▁kitap": PieceStats(count=10, crossing_count=1),
        },
        penalty_lambda=0.5,
        min_count=5,
        min_crossing_count=1,
        min_crossing_rate=0.5,
        min_surface_len=2,
        max_penalty=2.0,
        penalty_mode="rate",
    )

    assert len(adjustments) == 1
    assert adjustments[0].piece == "▁kitaplar"
    assert model.pieces[0].score == pytest.approx(-2.4)
    assert model.pieces[1].score == -1.0
