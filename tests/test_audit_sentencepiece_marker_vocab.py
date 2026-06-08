from pathlib import Path

from scripts.audit_sentencepiece_marker_vocab import audit_pieces
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER


def test_audit_pieces_counts_marker_vocab_shapes():
    row = audit_pieces(
        name="toy",
        model=Path("toy.model"),
        pieces=[
            "<unk>",
            SOFT_MARKER,
            f"{SOFT_MARKER}lar",
            f"kitap{SOFT_MARKER}",
            f"ki{SOFT_MARKER}tap",
            "ev",
        ],
        marker=SOFT_MARKER,
        max_examples=10,
    )

    assert row.vocab_size == 6
    assert row.marker_piece_count == 4
    assert row.exact_marker_count == 1
    assert row.marker_with_surface_count == 3
    assert row.marker_prefix_count == 1
    assert row.marker_suffix_count == 1
    assert row.marker_internal_count == 1
