from scripts.evaluate_v2_finite_protected_soft_marker_intrinsic import (
    append_marked_sp_segment,
    encode_finite_protected_soft_marker,
)
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER
from tr_tokenizer.tokenizer import WORD_START


class FakeSoftMarkerProcessor:
    def EncodeAsPieces(self, surface: str) -> list[str]:
        return ["\u2581" + surface]


def test_append_marked_sp_segment_recovers_suffix_tokens():
    tokens: list[str] = []
    count = append_marked_sp_segment(
        logical_tokens=tokens,
        surface=f"kitap{SOFT_MARKER}lar{SOFT_MARKER}dan",
        starts_after_space=True,
        processor=FakeSoftMarkerProcessor(),
    )

    assert count == 1
    assert tokens == [f"{WORD_START}kitap", "+lar", "+dan"]


def test_finite_protected_soft_marker_keeps_protected_and_suffix_tail():
    encoded = encode_finite_protected_soft_marker(
        "README.md'yi kitaplardan.",
        processor=FakeSoftMarkerProcessor(),
        selected_pieces=["README", ".md"],
    )

    assert f"{WORD_START}README.md" in encoded.logical_tokens
    assert "'" in encoded.logical_tokens
    assert "+yi" in encoded.logical_tokens
    assert "+lardan" in encoded.logical_tokens or "+lar" in encoded.logical_tokens
    assert encoded.protected_piece_tokens == 2
    assert encoded.protected_byte_tokens == 0
