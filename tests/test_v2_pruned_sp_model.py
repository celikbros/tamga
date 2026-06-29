import pytest
from sentencepiece import sentencepiece_model_pb2

from scripts.materialize_v2_pruned_sp_model import (
    in_scope,
    select_and_floor_pieces,
)
from scripts.materialize_v2_score_shifted_sp_model import PieceStats


def make_model(piece_scores):
    model = sentencepiece_model_pb2.ModelProto()
    for piece_name, score in piece_scores:
        piece = model.pieces.add()
        piece.piece = piece_name
        piece.score = score
    return model


def test_in_scope_filters_word_start_pieces():
    assert in_scope("▁kitap", "all")
    assert in_scope("lar", "all")
    assert in_scope("▁kitap", "word_start")
    assert not in_scope("lar", "word_start")
    assert not in_scope("▁kitap", "non_word_start")
    assert in_scope("lar", "non_word_start")


def test_select_and_floor_pieces_uses_train_crossing_thresholds():
    model = make_model(
        [
            ("▁kitaplar", -2.0),
            ("lar", -1.0),
            ("temiz", -3.0),
        ]
    )
    stats = {
        "▁kitaplar": PieceStats(count=20, crossing_count=20),
        "lar": PieceStats(count=20, crossing_count=5),
        "temiz": PieceStats(count=20, crossing_count=0),
    }

    selected = select_and_floor_pieces(
        model,
        stats,
        min_count=10,
        min_crossing_count=10,
        min_crossing_rate=0.7,
        min_surface_len=2,
        piece_scope="all",
        score_floor=-30.0,
    )

    assert [row.piece for row in selected] == ["▁kitaplar"]
    assert model.pieces[0].score == pytest.approx(-30.0)
    assert model.pieces[1].score == pytest.approx(-1.0)
    assert model.pieces[2].score == pytest.approx(-3.0)
