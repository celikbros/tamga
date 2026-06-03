from scripts.evaluate_v2_marker_stripped_diagnostic import (
    append_raw_sp_segment,
    encode_finite_protected_marker_stripped,
)
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER
from tr_tokenizer.tokenizer import WORD_START


class FakeProcessor:
    def EncodeAsPieces(self, surface: str) -> list[str]:
        return ["\u2581" + surface]


def test_append_raw_sp_segment_does_not_emit_soft_marker():
    tokens: list[str] = []
    count = append_raw_sp_segment(
        logical_tokens=tokens,
        surface="kitaplar",
        starts_after_space=True,
        processor=FakeProcessor(),
    )

    assert count == 1
    assert tokens == [f"{WORD_START}kitaplar"]
    assert SOFT_MARKER not in tokens[0]


def test_marker_stripped_encoder_preserves_protected_without_marker_insert():
    encoded = encode_finite_protected_marker_stripped(
        "README.md'yi kitaplardan.",
        processor=FakeProcessor(),
        selected_pieces=["README", ".md"],
    )

    joined = "".join(encoded.logical_tokens)
    assert SOFT_MARKER not in joined
    assert f"{WORD_START}README.md" in encoded.logical_tokens
    assert "'" in encoded.logical_tokens
    assert "+yi" in encoded.logical_tokens
    assert encoded.protected_piece_tokens == 2
    assert encoded.protected_byte_tokens == 0
