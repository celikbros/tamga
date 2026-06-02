from scripts.compare_tokenizers import boundary_score
from scripts.evaluate_v2_soft_marker_candidate_intrinsic import (
    encode_soft_marker_sentencepiece,
    raw_soft_marker_segments,
)
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER
from tr_tokenizer.tokenizer import WORD_START


class FakeProcessor:
    def EncodeAsPieces(self, text: str) -> list[str]:
        return ["▁" + text]


def test_raw_soft_marker_segments_insert_marker_at_soft_boundary():
    segments = raw_soft_marker_segments("kitaplardan geldim")

    assert segments[0].surface.startswith("kitap")
    assert SOFT_MARKER in segments[0].surface
    assert segments[-1].starts_after_space is True


def test_encode_soft_marker_sentencepiece_reads_marker_as_suffix_boundary():
    tokens = encode_soft_marker_sentencepiece("kitaplardan", FakeProcessor())

    assert tokens[0].startswith(WORD_START)
    assert any(token.startswith("+") for token in tokens[1:])


def test_soft_marker_boundary_can_score_against_suffix_gold():
    tokens = encode_soft_marker_sentencepiece("kitaplardan", FakeProcessor())
    gold = [f"{WORD_START}kitap", "+lar", "+dan"]

    assert boundary_score(tokens, gold).f1 == 1.0
