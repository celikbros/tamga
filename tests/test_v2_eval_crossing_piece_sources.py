from scripts.audit_v2_eval_crossing_piece_sources import (
    CrossingPieceSource,
    score_bucket,
    train_rate_bucket,
)


def test_train_rate_bucket_uses_train_stats_not_eval_stats():
    assert (
        train_rate_bucket(
            CrossingPieceSource(
                piece="x",
                train_count=100,
                train_crossing_count=100,
            ),
            min_reliable_count=20,
        )
        == "train_rate=1.00"
    )
    assert (
        train_rate_bucket(
            CrossingPieceSource(
                piece="x",
                train_count=100,
                train_crossing_count=75,
            ),
            min_reliable_count=20,
        )
        == "train_rate=0.70-0.99"
    )
    assert (
        train_rate_bucket(
            CrossingPieceSource(
                piece="x",
                train_count=3,
                train_crossing_count=3,
            ),
            min_reliable_count=20,
        )
        == "train_count< 20"
    )
    assert (
        train_rate_bucket(
            CrossingPieceSource(piece="x"),
            min_reliable_count=20,
        )
        == "no_train_stats"
    )


def test_score_bucket_separates_floor_from_counted_scores():
    assert score_bucket(-30.0, score_floor=-30.0, epsilon=1e-6) == "floor_score"
    assert score_bucket(-29.9999995, score_floor=-30.0, epsilon=1e-6) == "floor_score"
    assert score_bucket(-15.0, score_floor=-30.0, epsilon=1e-6) == "counted_score"
    assert score_bucket(None, score_floor=-30.0, epsilon=1e-6) == "score_missing"
