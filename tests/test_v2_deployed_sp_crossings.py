from scripts.audit_v2_deployed_sp_crossings import (
    PieceCrossingStats,
    audit_segment,
    bucket_rows,
    crossing_bucket,
)
from scripts.materialize_v2_score_shifted_sp_model import Segment


class FakeProcessor:
    def __init__(self, pieces):
        self._pieces = pieces

    def EncodeAsPieces(self, _surface):
        return list(self._pieces)


def test_crossing_bucket_labels_rates():
    assert crossing_bucket(1.0) == "1.00"
    assert crossing_bucket(0.8) == "0.70-0.99"
    assert crossing_bucket(0.5) == "0.40-0.69"
    assert crossing_bucket(0.3) == "0.20-0.39"
    assert crossing_bucket(0.1) == "0.00-0.19"
    assert crossing_bucket(0.0) == "0.00"


def test_audit_segment_counts_deployed_piece_crossings():
    stats: dict[str, PieceCrossingStats] = {}
    segment = Segment(surface="abcd", soft_boundaries=(2,))
    pieces, crossed, crossing_pieces, failures = audit_segment(
        segment,
        processor=FakeProcessor(["abcd"]),
        piece_stats=stats,
    )

    assert pieces == 1
    assert crossed == 1
    assert crossing_pieces == 1
    assert failures == 0
    assert stats["abcd"].count == 1
    assert stats["abcd"].crossing_count == 1


def test_bucket_rows_groups_crossing_damage():
    class Audit:
        crossed_boundaries = 10
        piece_stats = {
            "a": PieceCrossingStats(count=5, crossing_occurrences=5, crossing_count=5),
            "b": PieceCrossingStats(count=10, crossing_occurrences=3, crossing_count=3),
            "c": PieceCrossingStats(count=10, crossing_occurrences=0, crossing_count=0),
        }

    rows = bucket_rows(Audit())
    by_bucket = {row[0]: row for row in rows}

    assert by_bucket["1.00"][3] == 5
    assert by_bucket["0.20-0.39"][3] == 3
