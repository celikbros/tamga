import math
from collections import Counter

import pytest
from sentencepiece import sentencepiece_model_pb2

from scripts.materialize_v2_teacher_distilled_sp_model import apply_distilled_scores


def make_model(piece_scores):
    model = sentencepiece_model_pb2.ModelProto()
    for piece_name, score in piece_scores:
        piece = model.pieces.add()
        piece.piece = piece_name
        piece.score = score
    return model


def test_apply_distilled_scores_sets_log_relative_frequency_and_floor():
    model = make_model(
        [
            ("<unk>", 0.0),
            ("a", -1.0),
            ("b", -2.0),
            ("c", -3.0),
        ]
    )

    changed, total = apply_distilled_scores(
        model,
        Counter({"a": 3, "b": 1}),
        score_floor=-30.0,
    )

    assert total == 4
    assert changed == 3
    assert model.pieces[0].score == 0.0
    assert model.pieces[1].score == pytest.approx(math.log(3 / 4))
    assert model.pieces[2].score == pytest.approx(math.log(1 / 4))
    assert model.pieces[3].score == pytest.approx(-30.0)
