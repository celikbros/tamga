from scripts.audit_v2_1_sidecar_operation_simulation import (
    Span,
    TokenPiece,
    char_to_byte_offsets,
    interval_bytes,
    merge_intervals,
    protected_spans,
    span_mask,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line
from tr_tokenizer import TurkishTokenizer


def test_char_to_byte_offsets_handles_multibyte_text() -> None:
    text = "a çığ"

    offsets = char_to_byte_offsets(text)

    assert offsets == [0, 1, 2, 4, 6, 8]


def test_merge_intervals_merges_touching_ranges() -> None:
    intervals = [(5, 7), (1, 3), (3, 5), (10, 11)]

    merged = merge_intervals(intervals)

    assert merged == [(1, 7), (10, 11)]
    assert interval_bytes(merged) == 7


def test_span_mask_reports_boundary_overmask() -> None:
    span = Span(
        route="file_like",
        surface="bc",
        char_start=1,
        char_end=3,
        byte_start=1,
        byte_end=3,
    )
    tokens = [
        TokenPiece("ab", 0, 2, 0, 2),
        TokenPiece("cd", 2, 4, 2, 4),
    ]

    mask = span_mask(span, tokens)

    assert mask is not None
    assert mask.mask_start == 0
    assert mask.mask_end == 4
    assert mask.left_extra_bytes == 1
    assert mask.right_extra_bytes == 1
    assert mask.extra_bytes == 2
    assert mask.crossing_tokens == 2
    assert not mask.edge_aligned


def test_protected_spans_use_byte_offsets_for_percent_encoded_surface() -> None:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)

    spans = protected_spans("URL %20'si goruldu", tokenizer)

    assert any(
        span.route == "percent_encoded"
        and span.surface == "%20"
        and span.byte_len == 3
        for span in spans
    )


def test_analyze_line_preserves_literal_word_start_marker() -> None:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    text = "başlık ▁ dekor"

    pieces = analyze_line(text, tokenizer)

    assert "".join(piece.surface for piece in pieces) == text
    assert any(piece.surface == "▁" for piece in pieces)


def test_protected_spans_does_not_crash_on_literal_word_start_marker() -> None:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    text = "forum ▁ README.md"

    spans = protected_spans(text, tokenizer)

    assert "".join(piece.surface for piece in analyze_line(text, tokenizer)) == text
    assert any(span.route == "file_like" and span.surface == "README.md" for span in spans)
