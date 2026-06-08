from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER
from scripts.materialize_v2_train_only_marker_views import (
    build_marker_view,
    high_value_suffix_marker_indices,
    suffix_chain_marker_indices,
)


def _piece(surface: str, kind: str, boundary: str) -> dict[str, object]:
    return {"surface": surface, "kind": kind, "boundary_before": boundary}


def test_suffix_chain_policy_marks_only_multi_suffix_group():
    pieces = [
        _piece("kitap", "word_start", "hard"),
        _piece("lar", "suffix", "soft"),
        _piece("dan", "suffix", "soft"),
        _piece(" ", "whitespace", "hard"),
        _piece("ev", "word_start", "hard"),
        _piece("de", "suffix", "soft"),
    ]

    markers, groups, marked = suffix_chain_marker_indices(pieces, min_suffix_count=2)

    assert markers == {1, 2}
    assert groups == 2
    assert marked == 1

    train_view, segments, soft_total, marker_count, hard = build_marker_view(
        pieces,
        marker_indices=markers,
    )
    assert train_view == f"kitap{SOFT_MARKER}lar{SOFT_MARKER}dan evde"
    assert segments == 2
    assert soft_total == 3
    assert marker_count == 2
    assert hard == 3


def test_high_value_suffix_policy_marks_allowlisted_suffixes():
    pieces = [
        _piece("gel", "word_start", "hard"),
        _piece("iyor", "suffix", "soft"),
        _piece("um", "suffix", "soft"),
    ]

    markers = high_value_suffix_marker_indices(pieces, allowlist={"um"})

    assert markers == {2}
